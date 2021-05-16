import datetime

def to_datetime(string):
	datetime_obj = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
	datetime_obj = datetime_obj.replace(tzinfo = datetime.timezone.utc)

	return datetime_obj

def filter_transactions(json_data, history, init_datetime = None):
	swap_list = {}

	history_update = {}

	for transaction in json_data['data']:
		# used for initialization, stop loop once we parsed "todays" swaps
		if (not init_datetime == None) and (to_datetime(transaction['timestamp']) < init_datetime): break

		# validate if transaction is a user swapping CAD
		if (not transaction['type'] == 'peer') or (not transaction['currency'] == 'CAD'): continue

		# determine shaketag and id of swapper
		user_obj = transaction.get('to') or transaction['from']
		shaketag = user_obj['label']
		user_id = user_obj['id']

		swap = 1 if (transaction['direction'] == 'credit') else -1

		if (not shaketag in history):
			history[shaketag] = {
				'timestamp': transaction['timestamp'],
				'swap': swap,
				'user_id': user_id
			}
		else:
			is_newer = to_datetime(transaction['timestamp']) > to_datetime(history[shaketag]['timestamp'])

			# if the transaction ids are equal to history, that means we have already processed, stop loop
			if (init_datetime == None) and (not is_newer):
				break

			if (is_newer) and (not shaketag in history_update):
				# remember this transaction date for updating
				history_update[shaketag] = transaction['timestamp']

			# update swap counter
			history[shaketag]['swap'] = history[shaketag]['swap'] + swap

		# check if we need to add this transaction to the swap list
		if (history[shaketag]['swap'] > 0) and (transaction['direction'] == 'credit'):
			swap_list[shaketag] = swap_list.get(shaketag) or 0
			swap_list[shaketag] = swap_list[shaketag] + transaction['amount']
		elif (transaction['direction'] == 'debit'):
			if (shaketag in swap_list):
				swap_list[shaketag] = swap_list[shaketag] - transaction['amount']

				if (swap_list[shaketag] <= 0): del swap_list[shaketag]

	# finally update history timestamps
	for shaketag in history_update:
		history[shaketag]['timestamp'] = history_update[shaketag]

	return swap_list

def printt(msg):
	formatted_datetime = datetime.datetime.now().strftime('[%Y%m%d %H:%M:%S]')

	print('{} {}'.format(formatted_datetime, msg))