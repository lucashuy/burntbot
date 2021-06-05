import requests
import json

import globals

from service.requests.exception import raise_exception
from service.log import log

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
		('Something went wrong when swapping: {}'.format(response.text))

		raise_exception(response.status_code)

	return response

def get_transactions(body: dict) -> dict:
	# copy headers to append content type
	local_headers = globals.HEADERS.copy()
	local_headers['Content-Type'] = 'application/json'

	response = requests.post(globals.ENDPOINT_HISTORY, headers = local_headers, data = json.dumps(body))
	
	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching history: {}'.format(response.text))

		raise_exception(response.status_code)

	return response.json()