import requests

import globals

from api.exception import raise_exception
from utilities.log import log

def users(user_id: str) -> dict:
	response = requests.get(f'https://api.shakepay.com/users/{user_id}', headers = globals.headers, timeout = 5)

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching users: {}'.format(response.text))
		
		raise_exception(response.status_code)

	return response.json()

def search(shaketag: str) -> list:
	results = []

	local_shaketag = shaketag
	if (local_shaketag[0] == '@'): local_shaketag = shaketag[1:]

	if (shaketag != ''):
		response = requests.get(f'https://api.shakepay.com/users?username={local_shaketag}', headers = globals.headers, timeout = 5)

		if (not response.ok):
			log('Something went wrong when fetching users: {}'.format(response.text))
			
			raise_exception(response.status_code)

		response = response.json()['data']

		for obj in response:
			results.append(f'@{obj["username"]}')

	return results