import threading
import time
import traceback
import datetime

from api.transactions import get_transactions
from api.exception import ClientException
from utilities.datetime import get_swap_datetime, string_to_datetime
from utilities.log import log
from utilities.swap import swap
from utilities.transaction_parser import determine_userid, determine_shaketag
from classes.sqlite import SQLite

class SwapBot(threading.Thread):
	bot_state = 0

	def __init__(self):
		threading.Thread.__init__(self, daemon = True)

		self.restarts = 0
		self.last_restart = time.time()
		self.recent_transaction_datetime = None
		
	def _update_transaction(self, db, transaction):
		'''
		Helper function that updates the transaction and shaketag data IF the transaction is P2P and in CAD
		'''

		if (transaction['type'] == 'peer') and (transaction['currency'] == 'CAD'):
			user_id = determine_userid(transaction)
			shaketag = determine_shaketag(transaction)
			transaction_epoch = string_to_datetime(transaction['timestamp']).timestamp()

			# add/update shaketag in database and add transaction
			db.upsert_shaketag(user_id, shaketag, transaction_epoch)
			db.add_transcation(transaction)
	
	def _init_history(self) -> float:
		log('This might take a little')
		db = SQLite()

		# parameters for query
		params = {
			'currency': 'CAD',
			'limit': 2000,
			'before': datetime.datetime.now(datetime.timezone.utc)
		}

		# used to stop fetching transactions
		swapping_begin_datetime = get_swap_datetime()
		
		while (1):
			log(f'{params["before"]}', True)
			(response, headers) = get_transactions(params)

			# stop if we have all the results
			if (len(response) == 1): break

			# iterate results
			for transaction in response:
				transaction_datetime = string_to_datetime(transaction['timestamp'])

				# stop if the transaction is before swapping started
				if (transaction_datetime < swapping_begin_datetime): break

				self._update_transaction(db, transaction)

			# write changes
			db.commit()

			last_transaction_timestamp = response[-1]['timestamp']
			last_transaction_datetime = string_to_datetime(last_transaction_timestamp)

			# stop if we have transactions from before swapping
			if (last_transaction_datetime < swapping_begin_datetime): break

			# update time to fetch next page of transactions
			params['before'] = last_transaction_datetime

		db.close()

	def _do_returns(self, db: SQLite):
		'''
		Helper function to return swaps
		'''

		# get any returns
		returns = db.get_credits()

		if (len(returns) > 0):
			note = db.get_key_value('return_note', '')
			do_labrie_check = db.get_key_value('bot_return_check', False)

			# do returns
			for tuple in returns: swap(tuple[0], tuple[1], note, do_labrie_check)

	def run(self):
		log('Bot loading...')

		db = SQLite()

		# initialize database with swaps if it is empty
		if (db.get_paddle_swappers() == 0): self._init_history()

		# get the last transaction timestamp
		self.recent_transaction_datetime = db.get_last_transaction_epoch()

		params = {
			'currency': 'CAD',
			'limit': 2000,
			'since': self.recent_transaction_datetime.isoformat()
		}

		# get any transactions we might have missed between last bot usage and now
		while (1):
			(response, headers) = get_transactions(params)

			# update database with transactions
			for transaction in response: self._update_transaction(db, transaction)

			# write changes
			db.commit()

			# save the most recent transaction timestamp for next fetch
			if (len(response) > 0): params['since'] = string_to_datetime(response[0]['timestamp']).isoformat()

			log(f'Fetching old data ({params["since"]}) ({len(response)})', True)

			# stop if we get a result with less than 2000 results, indicating all caught up
			if (len(response) < 2000):
				log(f'Done fetching', True)
				break

		# do any late returns
		log('Checking for late returns')
		self._do_returns(db)

		# bot ready
		log('Bot ready')
		SwapBot.bot_state = 1

		while (1):
			try:
				# start polling
				(response, headers) = get_transactions(params)

				# save transactions in db
				for transaction in response: self._update_transaction(db, transaction)

				# write changes
				db.commit()

				# do returns
				self._do_returns(db)

				if (len(response) > 0):
					# update next transaction time if we have items in the list
					params['since'] = string_to_datetime(response[0]['timestamp']).isoformat()
				elif (len(response) == 0):
					# stop the bot, something weird happened
					log('Unexpected data, stopping bot')

					db.close()

					raise SystemExit(0)

				time.sleep(db.get_key_value('poll_rate'))
			except ClientException:
				log('Bot stopped because of a token issue (did you logout of all devices?)')

				db.close()

				raise SystemExit(0)
			except Exception as e:
				SwapBot.bot_state = 0

				log(f'Bot stopped due to: {e}')
				log(traceback.format_exc())

				time_now = time.time()

				# if bot last restart was > 10 minutes ago, reset counter
				if (self.last_restart + (60 * 10) < time_now):
					self.restarts = 0

				if (self.restarts > 5):
					log('Bot stopped five times in 10 minutes, stopping program')
					
					db.close()
					
					raise SystemExit(0)
				else:
					log(f'Bot restarting after 60 seconds')

					self.restarts = self.restarts + 1
					self.last_restart = time_now

					time.sleep(60)

					SwapBot.bot_state = 1