import threading
import time

import globals
import logic_requests
import logic_service

from dotenv import load_dotenv
load_dotenv()

class Map(dict):
	def __missing__(self, key): return key

class SwapBot(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)

		self.restarts = 0
		self.last_restart = time.time()

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
			logic_service.printt(f'Fetching page {body["pagination"]["page"]} of transactions')

			response = logic_requests.transactions(body)
			data = response['data']

			if (len(data) == 0): break

			logic_service.populate_history(data)
			
			body['pagination']['page'] = body['pagination']['page'] + 1

			# prevent rate limit by ensuring we maintain window between fetches
			time_left = 10 - (int(time.time()) - last_time)
			if (time_left > 0):
				time.sleep(time_left)

			last_time = int(time.time())

	def swap(self, shaketag, amount):
		note = globals.NOTE.format_map(Map(shaketag = shaketag, amount = '${}'.format(amount)))

		logic_service.printt('Sending ${} to {}'.format(amount, shaketag))
		logic_requests.send_transaction(amount, shaketag, note)
		
		# logic_service.printt(f'Simulate sending ${amount} to {shaketag} with note: ({note})')

	def poll_shakepay(self):
		while (1):
			response_json = logic_requests.transactions({'filterParams': {'currencies': ['CAD']}})
			swap_list = logic_service.get_swaps(response_json['data'])

			for shaketag in swap_list:
				amount = globals.HISTORY[shaketag]['swap']
				
				self.swap(shaketag, amount)
				
			time.sleep(globals.POLL_RATE)

	def run(self):
		# init hash table of transactions
		logic_service.printt('Initializing swap history today')
		self.init_history()

		for shaketag in globals.HISTORY:
			amount = globals.HISTORY[shaketag]['swap']
			if (amount > 0.):
				self.swap(shaketag, amount)

		# wait for rate limit cooldown (for transactions its 15/minute)
		logic_service.printt('Waiting 60 seconds for rate limit expiry')
		time.sleep(60)

		while (self.restarts < 3):
			try:
				logic_service.printt('Bot ready')

				# start polling
				self.poll_shakepay()
			except logic_requests.ClientException:
				logic_service.printt('ENCOUNTERED CLIENT 4xx ERROR')

				break
			except logic_requests.OtherException:
				logic_service.printt(f'ENCOUNTERED OTHER ERROR, RESTARTING (fails in past 5 mins: {self.restarts})')

				time_now = time.time()

				# checks to see if we restarted recently (5 min window), if not then reset counter
				if (time_now - self.last_restart >= (60 * 5)):
					self.restarts = 0

				self.restarts = self.restarts + 1
				self.last_restart = time_now