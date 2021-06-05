import requests

import globals

from service.requests.exception import raise_exception
from service.log import log

def get_wallet():
	response = requests.get(globals.ENDPOINT_WALLET, headers = globals.HEADERS)

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching wallets: {}'.format(response.text))
		
		raise_exception(response.status_code)

	data = response.json()['data']
	for wallet in data:
		if (wallet['currency'] == 'CAD'):
			return wallet