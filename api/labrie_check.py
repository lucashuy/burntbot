import requests

import globals

def labrie_check(shaketag: str, type: str) -> dict:
	data =  {
		'source': globals.headers['X-Device-Unique-Id'],
		'shaketag': shaketag,
		'step': type
	}

	response = requests.post('https://swap.labrie.ca/api/', json = data)

	if (response.ok):
		response = response.json()
	else:
		response = {'success': False}

	return response
