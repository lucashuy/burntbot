import requests
import json

import logic_service
import globals

"""
Returns your CAD wallet ID
"""
def wallet():
	response = requests.get(globals.ENDPOINT_WALLET, headers = globals.HEADERS)

	# make sure we have 2xx status
	if (not response.ok):
		logic_service.printt('Something went wrong when fetching wallets: {}'.format(response.text))
		raise SystemExit(0)

	data = response.json()['data']
	for wallet in data:
		if (wallet['currency'] == 'CAD'):
			return wallet['id']

"""
Sends a transaction
"""
def send_transaction(amount: float, shaketag: str, note: str) -> dict:
	# copy headers to append content type
	local_headers = globals.HEADERS.copy()
	local_headers['Content-Type'] = 'application/json'

	body = {
		'amount': str(amount),
		'fromWallet': globals.WALLET_ID,
		'note': note,
		'to': shaketag[1:],
		'toType': 'user'
	}

	response = requests.post(globals.ENDPOINT_SWAP, headers = local_headers, data = json.dumps(body))
	
	# make sure we have 2xx status
	if (not response.ok):
		logic_service.printt('Something went wrong when swapping: {}'.format(response.text))
		raise SystemExit(0)

	return response

"""
Returns a history of CAD transactions
"""
def transactions(body: dict) -> dict:
	# copy headers to append content type
	local_headers = globals.HEADERS.copy()
	local_headers['Content-Type'] = 'application/json'

	response = requests.post(globals.ENDPOINT_HISTORY, headers = local_headers, data = json.dumps(body))
	
	# make sure we have 2xx status
	if (not response.ok):
		logic_service.printt('Something went wrong when fetching history: {}'.format(response.text))
		raise SystemExit(0)

	return response.json()