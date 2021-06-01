import requests
import json

import logic_service
import globals

class ClientException(Exception): pass
class OtherException(Exception): pass

def raise_exception(status_code: int):
	if (str(status_code)[0] == 4):
		raise ClientException()
	else:
		raise OtherException()

"""
Authenticates
"""
def login(email: str, password: str, code: str) -> str:
	# copy headers to append content type
	local_headers = globals.HEADERS.copy()
	local_headers['Content-Type'] = 'application/json'

	# pre 2FA POST
	response = requests.post(globals.ENDPOINT_AUTHENTICATE, headers = local_headers, data = json.dumps({
		'password': password,
		'strategy': 'local',
		'totpType': 'sms',
		'username': email
	}))

	# make sure we have 2xx status
	if (not response.ok):
		logic_service.printt('Something went wrong when login (pre 2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()

	local_headers['Authorization'] = response['accessToken']

	# 2FA POST
	response = requests.post(globals.ENDPOINT_AUTHENTICATE, headers = local_headers, data = json.dumps({
		'mfaToken': code,
		'strategy': 'mfa'
	}))

	# make sure we have 2xx status
	if (not response.ok):
		logic_service.printt('Something went wrong when login (2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()

	return response['accessToken']

"""
Returns your CAD wallet ID
"""
def wallet():
	response = requests.get(globals.ENDPOINT_WALLET, headers = globals.HEADERS)

	# make sure we have 2xx status
	if (not response.ok):
		logic_service.printt('Something went wrong when fetching wallets: {}'.format(response.text))
		
		raise_exception(response.status_code)

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

		raise_exception(response.status_code)

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

		raise_exception(response.status_code)

	return response.json()