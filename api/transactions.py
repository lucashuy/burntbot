import requests
import json

import globals

from api.exception import raise_exception
from utilities.log import log

def send_transaction(amount: float, shaketag: str, note: str) -> dict:
	# copy headers to append content type
	local_headers = globals.headers.copy()
	local_headers['Content-Type'] = 'application/json'

	body = {
		'amount': str(amount),
		'fromWallet': globals.wallet_id,
		'note': note,
		'to': shaketag[1:],
		'toType': 'user'
	}

	response = requests.post(globals.endpoint_swap, headers = local_headers, data = json.dumps(body))
	
	# make sure we have 2xx status
	if (not response.ok):
		('Something went wrong when swapping: {}'.format(response.text))

		raise_exception(response.status_code)

	return response

def get_transactions(params: dict) -> tuple:
	# copy headers to append content type
	local_headers = globals.headers.copy()
	
	response = requests.get(globals.endpoint_history, headers = local_headers, params = params)
	headers = response.headers

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching history: {}'.format(response.text))

		raise_exception(response.status_code)

	return (response.json(), headers)