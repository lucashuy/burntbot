import requests

import globals

from api.exception import raise_exception
from utilities.log import log

def get_wallet():
	response = requests.get('https://api.shakepay.com/wallets', headers = globals.headers, timeout = 5)

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching wallets: {}'.format(response.text))
		
		raise_exception(response.status_code)

	data = response.json()['data']
	for wallet in data:
		if (wallet['currency'] == 'CAD'):
			return wallet