import requests

import globals

from api.waitlist import update_waitlist

def heart_beat():
	update_waitlist()

	data =  {
		'guid': globals.headers['X-Device-Unique-Id'],
		'shaketag': globals.shaketag,
		'metadata': {
			'position': globals.waitlist_position,
			'points': globals.waitlist_points,
			'swapsToday': globals.waitlist_swaps
		}
	}

	requests.post('https://swap.labrie.ca/api/ping/', json = data, timeout = 5)