import threading
import time
import traceback
import datetime

import globals

from api.transactions import get_transactions
from api.exception import ClientException
from utilities.transaction_parser import populate_history, get_swaps
from utilities.datetime import get_swap_datetime, string_to_datetime
from utilities.persistence import upsert_persistence
from utilities.log import log
from utilities.swap import swap

class SwapBot(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)

		self.restarts = 0
		self.last_restart = time.time()
		self.recent_transaction_datetime = None

	def _offset_timestamp(self, timestamp: str, offset: int) -> datetime.datetime:
		return string_to_datetime(timestamp) + datetime.timedelta(milliseconds = offset)

	def init_history(self) -> float:
		params = {
			'currency': 'CAD',
			'limit': 2000,
			'before': datetime.datetime.now(datetime.timezone.utc)
		}

		swapping_begin_datetime = get_swap_datetime()
		
		log(f'Fetching your transactions...')

		while (1):
			(response, headers) = get_transactions(params)

			# stop if we have an empty list
			if (len(response) == 0): break

			populate_history(response)

			# save the most recent transaction's timestamp for use in polling later
			if (self.recent_transaction_datetime == None):
				self.recent_transaction_datetime = self._offset_timestamp(response[0]['timestamp'], 1)

			# check if we need to stop fetching history
			last_transaction_timestamp = response[-1]['timestamp']
			last_transaction_datetime = string_to_datetime(last_transaction_timestamp)

			log(f'{last_transaction_datetime} vs {swapping_begin_datetime}', True)
			if (last_transaction_datetime < swapping_begin_datetime):
				break

			params['before'] = self._offset_timestamp(last_transaction_timestamp, -1)

	def run(self):
		while (1):
			try:
				# init hash table of transactions
				log('Initializing swap history today')
				self.init_history()

				# adjust swaps by our blacklist function
				for shaketag, amount in globals.bot_blacklist.items():
					pass

				# iterate through transactions and apply adjustments and pay back those need swaps
				# instead of adjust, then swap, do it together, saves CPU time
				for _, history in globals.bot_history.items():
					shaketag = history.get_shaketag()

					if (shaketag in globals.bot_blacklist):
						history.adjust_swap(globals.bot_blacklist[shaketag])

					amount = history.get_swap()

					if (amount != 0.): log(f'{shaketag}\twith\t{amount}\t{history.get_timestamp()}', True)

					if (amount > 0.):
						log(f'Late send ${amount} to {shaketag} ({history.get_timestamp()})')
						swap(shaketag, amount)

				log('Bot ready')

				globals.bot_state = 1

				# start polling
				while (1):
					params = {
						'currency': 'CAD',
						'limit': 2000,
						'since': self.recent_transaction_datetime.isoformat()
					}

					(response, headers) = get_transactions(params)
					swap_list = get_swaps(response)

					for userid in swap_list:
						user_details = globals.bot_history[userid]
						
						shaketag = user_details.get_shaketag()
						amount = user_details.get_swap()
						
						swap(shaketag, amount)

					# update next transaction time if we have items in the list
					if (len(response) > 0):
						self.recent_transaction_datetime = self._offset_timestamp(response[0]['timestamp'], 1)

					time.sleep(globals.bot_poll_rate)
			except ClientException:
				log('Bot died due to HTTP client error, stopping')
				upsert_persistence({'token': ''})

				raise SystemExit(0)
			except Exception as e:
				globals.bot_state = 0

				log(f'Crashed due to: {e}')
				log(traceback.format_exc())

				globals.bot_history = {}

				time_now = time.time()

				# if bot last restart was > 10 minutes ago, reset counter
				if (self.last_restart + (60 * 10) < time_now):
					self.restarts = 0

				if (self.restarts > 3):
					log('Bot died from too many deaths, stopping')
					
					raise SystemExit(0)
				else:
					log('Bot died due to uncaught exception, restarting after 60 seconds')

					self.restarts = self.restarts + 1
					self.last_restart = time_now

					time.sleep(60)
