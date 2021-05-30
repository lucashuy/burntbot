import datetime

import globals

# should be using a class
def create_history(shaketag: str, timestamp: str, swap: int):
	globals.HISTORY[shaketag] = {
		'timestamp': timestamp,
		'swap': swap
	}

# determine shaketag and id of swapper
def determine_shaketag(transaction: dict) -> str:
	return (transaction.get('to') or transaction['from'])['label']

def determine_swap_amnt(transaction: dict) -> float:
	swap = 1. if (transaction['direction'] == 'credit') else -1.
	swap = swap * float(f'{transaction["amount"]:.2f}')

	return swap

def populate_history(data: list):
	for transaction in data:
		shaketag = determine_shaketag(transaction)
		swap = determine_swap_amnt(transaction)

		if (not shaketag in globals.HISTORY):
			# safe to assume that if the shaketag is NOT in history, this will be the most recent transaction from this person
			# create history entry for them
			create_history(shaketag, transaction['timestamp'], swap)
		else:
			# otherwise, update their swap amount
			globals.HISTORY[shaketag]['swap'] = globals.HISTORY[shaketag]['swap'] + swap

# this function is a bit of a mess since it also modifies the history (swap key)
def get_swaps(data: dict) -> dict:
	swap_list = {}
	history_updated = {}

	for transaction in data:
		# skip transaction if its not a swap in CDN
		if (not transaction['type'] == 'peer') or (not transaction['currency'] == 'CAD'): continue

		shaketag = determine_shaketag(transaction)
		swap = determine_swap_amnt(transaction)

		if (not shaketag in globals.HISTORY):
			# create new history entry for this swapper
			create_history(shaketag, transaction['timestamp', swap])
		else:
			# stop loop if we come across existing transaction by checking transaction times
			# since its a string, dont need to convert
			if (transaction['timestamp'] == globals.HISTORY[shaketag]['timestamp']):
				break

			# entry exists, update their swap
			globals.HISTORY[shaketag]['swap'] = globals.HISTORY[shaketag]['swap'] + swap

			# update the transaction history if we havent already
			if (not shaketag in history_updated):
				history_updated[shaketag] = transaction['timestamp']

		# check if we need to add to the swap list
		if (transaction['direction'] == 'credit'):
			swap_list[shaketag] = True

	# update swap list incase we also got returns from after we added the swap
	for shaketag in swap_list.copy():
		# remove name from list if we dont owe them
		if (globals.HISTORY[shaketag]['swap'] <= 0.):
			del swap_list[shaketag]

	# commit changes to user timestamp
	for shaketag, timestamp in history_updated.items():
		globals.HISTORY[shaketag]['timestamp'] = timestamp

	return swap_list

def printt(msg: str):
	formatted_datetime = datetime.datetime.now().strftime('[%Y%m%d %H:%M:%S]')

	print('{} {}'.format(formatted_datetime, msg))