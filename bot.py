import threading
import time
import traceback

import globals

from service.requests.transactions import get_transactions, send_transaction
from service.requests.labrie_check import labrie_check
from service.requests.exception import ClientException
from service.transaction_parser import populate_history, get_swaps
from service.datetime import get_swap_datetime, string_to_datetime
from service.persistence import upsert_persistence
from service.log import log

class Map(dict):
	def __missing__(self, key): return key

class SwapBot(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)

		self.restarts = 0
		self.last_restart = time.time()

	def init_history(self) -> float:
		# rowsPerPage other than 2000 breaks FOR SOME REASON
		body = {
			'filterParams': {'type': 'peer'},
			'pagination': {
				'descending': True,
				'page': 1,
				'rowsPerPage': 2000
			}
		}

		swapping_begin_datetime = get_swap_datetime()
		last_time = int(time.time())
		rate_limit_timeout = 0

		while (1):
			log(f'Fetching page {body["pagination"]["page"]} of transactions')

			(response, headers) = get_transactions(body)
			data = response['data']

			if (len(data) == 0): break

			populate_history(data)
			
			rate_limit_timeout = headers['Retry-After']

			# check if we need to stop fetching history
			log(f'{data[-1]["timestamp"]} vs {swapping_begin_datetime}', True)
			if (string_to_datetime(data[-1]['timestamp']) < swapping_begin_datetime):
				break

			body['pagination']['page'] = body['pagination']['page'] + 1

			# prevent rate limit by ensuring we maintain window between fetches
			time_left = 5 - (int(time.time()) - last_time)
			if (time_left > 0):
				time.sleep(time_left)

			last_time = int(time.time())

		return rate_limit_timeout

	def swap(self, shaketag, amount):
		note = globals.note.format_map(Map(shaketag = shaketag, amount = '${}'.format(amount)))

		if (globals.flags['listen']):
			log(f'Simulate sending ${amount} to {shaketag} with note: ({note})', True)
		else:
			response = labrie_check(shaketag, 'return')

			if (response['success']) and (response['data']['allow_return']):
				log(f'Sending ${amount} to {shaketag}', True)
				send_transaction(amount, shaketag, note)
			else:
				log(f'Ignoring auto return for {shaketag} for reason: {response["data"]["reason"] or ""}')

	def run(self):
		while (1):
			try:
				# init hash table of transactions
				log('Initializing swap history today')
				wait_time = self.init_history()

				# adjust swaps by our blacklist function
				for shaketag, amount in globals.blacklist.items():
					pass

				# iterate through transactions and apply adjustments and pay back those need swaps
				# instead of adjust, then swap, do it together, saves CPU time
				for _, history in globals.history.items():
					shaketag = history.get_shaketag()

					if (shaketag in globals.blacklist):
						history.adjust_swap(globals.blacklist[shaketag])

					amount = history.get_swap()

					if (amount != 0.): log(f'{shaketag}\twith\t{amount}\t{history.get_timestamp()}', True)

					if (amount > 0.):
						log(f'Late send ${amount} to {shaketag} ({history.get_timestamp()})')
						self.swap(shaketag, amount)

				# this isnt 100% accurate since there maybe late send backs
				log(f'Waiting {wait_time} seconds for rate limit expiry')
				time.sleep(float(wait_time))

				log('Bot ready')

				# start polling
				while (1):
					(response_json, headers) = get_transactions({'filterParams': {'currencies': ['CAD']}})
					swap_list = get_swaps(response_json['data'])

					for userid in swap_list:
						user_details = globals.history[userid]
						
						shaketag = user_details.get_shaketag()
						amount = user_details.get_swap()
						
						self.swap(shaketag, amount)
						
					time.sleep(globals.poll_rate)
			except ClientException:
				log('Bot died due to HTTP client error, stopping')
				upsert_persistence({'token': ''})

				raise SystemExit(0)
			except Exception as e:
				log(f'Crashed due to: {e}')
				log(traceback.format_exc())

				globals.history = {}

				time_now = time.time()

				# if bot last restart was > 10 minutes ago, reset counter
				if (self.last_restart + (60 * 10) < time_now):
					self.restarts = 0

				if (self.restarts > 5):
					log('Bot died from too many deaths, stopping')
					
					raise SystemExit(0)
				else:
					log('Bot died due to uncaught exception, restarting after 60 seconds')

					self.restarts = self.restarts + 1
					self.last_restart = time_now

					time.sleep(60)
