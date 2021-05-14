import datetime

FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

def filter_transactions(json_data, history, init_datetime = None):
	data = json_data['data']
	
	send_list = []

	for transaction in data:
		if (not transaction['type'] == 'peer'): continue
		if (not transaction['currency'] == 'CAD'): continue

		# only used for initializing history
		#TODO rewrite below if to function better
		if (not init_datetime == None):
			transaction_datetime = datetime.datetime.strptime(transaction['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
			transaction_datetime = transaction_datetime.replace(tzinfo = datetime.timezone.utc)

			if (transaction_datetime < init_datetime): break

		# get shaketag (this includes the @)
		user = (transaction.get('to', 0) or transaction['from'])['label']

		# temporary variable
		swap = 1 if transaction['direction'] == 'credit' else -1

		if (not user in history):
			# user not in history, add user to history table
			history[user] = {
				'transaction_id': transaction['transactionId'],
				'swap': swap
			}
		elif (history[user]['transaction_id'] == transaction['transactionId']):
			# user exists, check transaction_id to make sure its not the same transaction
			# we assume if we encounter same ID, we have reached the end of new swaps
			break

		# increment/decrement swap counter only if we didnt just add new history
		if (not history[user]['transaction_id'] == transaction['transactionId']): history[user]['swap'] = history[user]['swap'] + swap

		# check if we need to owe this user (if swap > 0, we owe, remember 0 is even and -1 is waiting)
		if (transaction['direction'] == 'credit' and history[user]['swap'] > 0):
			send_list.append(transaction)

	return send_list