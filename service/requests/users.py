import requests

import globals

from service.requests.exception import raise_exception
from service.log import log

def users(user_id: str) -> dict:
	response = requests.get(f'{globals.endpoint_users}/{user_id}', headers = globals.headers)

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching wallets: {}'.format(response.text))
		
		raise_exception(response.status_code)

	return response.json()