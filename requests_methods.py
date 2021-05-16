import requests
import json

import service

"""
Returns your CAD wallet ID
"""
def wallet(url, base_headers, token):
	# copy headers
	local_headers = base_headers.copy()
	local_headers['Authorization'] = token

	response = requests.get(url, headers = local_headers)

	# make sure we have 2xx status
	if (not response.ok):
		service.printt('Something went wrong when fetching wallets: {}'.format(response.text))
		raise SystemExit(0)

	data = response.json()['data']
	for wallet in data:
		if (wallet['currency'] == 'CAD'):
			return wallet['id']

def send_transaction(url, base_headers, token, amount, wallet_id, shaketag, note):
	# copy headers
	local_headers = base_headers.copy()
	local_headers['Content-Type'] = 'application/json'
	local_headers['Authorization'] = token

	body = {
		'amount': str(amount),
		'fromWallet': wallet_id,
		'note': note,
		'to': shaketag[1:],
		'toType': 'user'
	}

	response = requests.post(url, headers = local_headers, data = json.dumps(body))
	
	# make sure we have 2xx status
	if (not response.ok):
		service.printt('Something went wrong when swapping: {}'.format(response.text))
		raise SystemExit(0)

"""
Returns a history of CAD transactions
"""
def history(url, base_headers, token, body):
	# copy headers
	local_headers = base_headers.copy()
	local_headers['Content-Type'] = 'application/json'
	local_headers['Authorization'] = token

	response = requests.post(url, headers = local_headers, data = json.dumps(body))
	
	# make sure we have 2xx status
	if (not response.ok):
		service.printt('Something went wrong when fetching history: {}'.format(response.text))
		raise SystemExit(0)

	return response.json()