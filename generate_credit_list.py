def generate_credit_list(json_data):
	data = json_data['data']

	debts = {}

	for transaction in data:
		if (not transaction['type'] == 'peer'): continue

		user = (transaction.get('to', 0) or transaction['from'])['label']

		if (user in debts):
			del debts[user]
		else:
			debts[user] = transaction

	for user in debts.copy():
		debt = debts[user]

		if (debt['direction'] == 'debit'): del debts[user]

	return debts