import globals

from classes.user_history import UserHistory
from utilities.datetime import string_to_datetime, get_swap_datetime
from utilities.transaction_helper import determine_shaketag, determine_swap_amnt, determine_userid
from utilities.log import log

def create_history(userid: str, shaketag: str, timestamp: str, swap: float):
	globals.bot_history[userid] = UserHistory(shaketag, timestamp, swap)

def check_no_return(transaction: dict, userid: str, swap: float):
	# check if the note contains "no return"
	if ('no return' == transaction['note']):
		globals.bot_history[userid].adjust_swap(-swap)

def populate_history(data: list):
	for transaction in data:
		if (string_to_datetime(transaction['timestamp']) < get_swap_datetime): break

		userid = determine_userid(transaction)
		shaketag = determine_shaketag(transaction)
		swap = determine_swap_amnt(transaction)

		if (not userid in globals.bot_history):
			# safe to assume that if the shaketag is NOT in history, this will be the most recent transaction from this person
			# create history entry for them
			create_history(userid, shaketag, transaction['timestamp'], swap)
		else:
			history = globals.bot_history[userid]

			# otherwise, update their swap amount if this transaction does not exist
			if (not history.transaction_exists(transaction['transactionId'])):
				history.adjust_swap(swap)

		check_no_return(transaction, userid, swap)
		globals.bot_history[userid].add_prev_transaction(transaction)

# this function is a bit of a mess since it also modifies the history (swap key)
def get_swaps(data: dict) -> dict:
	swap_list = {}
	history_updated = {}

	for transaction in data:
		# skip transaction if its not a swap in CDN
		if (not transaction['type'] == 'peer') or (not transaction['currency'] == 'CAD'): continue

		userid = determine_userid(transaction)
		shaketag = determine_shaketag(transaction)
		swap = determine_swap_amnt(transaction)

		if (not userid in globals.bot_history):
			# create new history entry for this swapper
			create_history(userid, shaketag, transaction['timestamp'], swap)

			log(f'Create new entry for {shaketag} ({userid})', True)
		else:
			# stop loop if we come across existing transaction by checking if their transaction exists
			if (globals.bot_history[userid].transaction_exists(transaction['transactionId'])):
				break

			log(f'Adjust {shaketag} {globals.bot_history[userid].get_swap()} by {swap}', True)

			# entry exists, update their swap
			globals.bot_history[userid].adjust_swap(swap)

		# update the transaction history if we havent already
		if (not userid in history_updated):
			history_updated[userid] = (shaketag, transaction['timestamp'])

		# check if we need to add to the swap list
		if (transaction['direction'] == 'credit'):
			swap_list[userid] = True

		check_no_return(transaction, userid, swap)
		globals.bot_history[userid].add_prev_transaction(transaction)

	# update swap list incase we also got returns from after we added the swap
	for userid in swap_list.copy():
		# remove name from list if we dont owe them
		if (globals.bot_history[userid].get_swap() <= 0.):
			del swap_list[userid]

	# commit changes to user details
	for userid, data_tuple in history_updated.items():
		globals.bot_history[userid].update_shaketag(data_tuple[0])
		globals.bot_history[userid].update_timestamp(data_tuple[1])

	return swap_list
