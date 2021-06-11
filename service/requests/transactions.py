import requests
import json

import globals

from service.requests.exception import raise_exception
from service.log import log

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

def get_transactions(body: dict) -> tuple:
	# copy headers to append content type
	local_headers = globals.headers.copy()
	local_headers['Content-Type'] = 'application/json'

	response = requests.post(globals.endpoint_history, headers = local_headers, data = json.dumps(body))
	headers = response.headers

	log(f'{headers["Retry-After"]}s := {headers["X-RateLimit-Remaining"]}', True)

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching history: {}'.format(response.text))

		raise_exception(response.status_code)

	return (response.json(), headers)