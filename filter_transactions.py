import datetime

def to_datetime(string):
	datetime_obj = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
	datetime_obj = datetime_obj.replace(tzinfo = datetime.timezone.utc)

	return datetime_obj

def filter_transactions(json_data, history, init_datetime = None):
	data = json_data['data']
	
	send_list = []

	for transaction in data:
		if (not transaction['type'] == 'peer' or not transaction['currency'] == 'CAD'): continue

		transaction_datetime = to_datetime(transaction['timestamp'])

		# only used for initializing history
		#TODO rewrite below if to function better
		if (not init_datetime == None) and (transaction_datetime < init_datetime): break

		# get shaketag (this includes the @)
		user = (transaction.get('to', 0) or transaction['from'])['label']

		# temporary variable
		swap = 1 if transaction['direction'] == 'credit' else -1

		if (not user in history):
			# user not in history, add user to history table
			print('add {} with {}'.format(user, swap))
			history[user] = {
				'datetime': transaction_datetime,
				'swap': swap
			}
		elif (history[user]['datetime'] == transaction_datetime):
			# we reached an existing transaction, meaning we dont have new swaps
			break
		elif (history[user]['datetime'] > transaction_datetime):
			print('change {} from {} to {}'.format(user, history[user]['swap'], history[user]['swap'] + swap))

			if (init_datetime == None): history[user]['datetime'] = transaction_datetime
			history[user]['swap'] = history[user]['swap'] + swap

		# check if we need to owe this user (if swap > 0, we owe, remember 0 is even and -1 is waiting)
		if (transaction['direction'] == 'credit' and history[user]['swap'] > 0):
			send_list.append(transaction)

	return send_list