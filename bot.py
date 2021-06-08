import threading
import time

import globals

from service.requests.transactions import get_transactions, send_transaction
from service.requests.labrie_check import labrie_check
from service.requests.exception import ClientException
from service.persistence import upsert_persistence
from service.transaction_parser import populate_history, get_swaps
from service.log import log

class Map(dict):
	def __missing__(self, key): return key

class SwapBot(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)

		self.status = 0

		# init hash table of transactions
		log('Initializing swap history today')
		self.init_history()

		# send back to those that sent to us during bot startup/downtime
		for shaketag, history in globals.history.items():
			amount = history.get_swap()
			if (amount > 0.):
				log(f'Late send ${amount} to {shaketag} ({history.get_timestamp()})')
				self.swap(shaketag, amount)

		# wait for rate limit cooldown (for transactions its 15/minute)
		log('Waiting 60 seconds for rate limit expiry')
		time.sleep(60)

	def init_history(self):
		body = {
			'filterParams': {'type': 'peer'},
			'pagination': {
				'descending': True,
				'page': 1,
				'rowsPerPage': 2000
			}
		}

		last_time = int(time.time())

		while (1):
			log(f'Fetching page {body["pagination"]["page"]} of transactions')

			response = get_transactions(body)
			data = response['data']

			if (len(data) == 0): break

			populate_history(data)
			
			body['pagination']['page'] = body['pagination']['page'] + 1

			# prevent rate limit by ensuring we maintain window between fetches
			time_left = 6 - (int(time.time()) - last_time)
			if (time_left > 0):
				time.sleep(time_left)

			last_time = int(time.time())

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

	def poll_shakepay(self):
		while (1):
			response_json = get_transactions({'filterParams': {'currencies': ['CAD']}})
			swap_list = get_swaps(response_json['data'])

			for shaketag in swap_list:
				amount = globals.history[shaketag].get_swap()
				
				self.swap(shaketag, amount)
				
			time.sleep(globals.poll_rate)

	def run(self):
		try:
			log('Bot ready')

			# start polling
			self.poll_shakepay()
		except ClientException:
			log('ENCOUNTERED CLIENT 4xx ERROR')

			upsert_persistence({'token': ''})

			self.status = -1
		except:
			log(f'ENCOUNTERED OTHER ERROR, RESTARTING')

			self.status = 1