import requests

import globals

def heart_beat():
	data =  {
		'uid': globals.user_id,
		'guid': globals.headers['X-Device-Unique-Id'],
		'shaketag': globals.shaketag
	}

	requests.post('https://swap.labrie.ca/api/ping/', json = data)