import requests

import globals

from api.exception import raise_exception
from utilities.log import log
from utilities.datetime import get_reset_datetime, string_to_datetime

def update_waitlist():
	'''
	Update the local cache containing waitlist details (position, points, etc)
	'''
	
	local_headers = globals.headers.copy()

	# use etags to prevent redundant data transfer
	if (globals.waitlist_etag): local_headers['If-None-Match'] = globals.waitlist_etag

	# accept gzip compression (since those with lots of swaps have huge responses, > 3MB)
	local_headers['Accept-Encoding'] = 'gzip, deflate'

	response = requests.get('https://api.shakepay.com/card/waitlist', headers = local_headers)

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching waitlist data: {}'.format(response.text))
		
		raise_exception(response.status_code)

	# save etag for future
	globals.waitlist_etag = response.headers['ETag']

	if (response.status_code == 200):
		log('waitlist function has new data', True)

		data = response.json()

		globals.waitlist_points = data['score']
		globals.waitlist_position = data['rank']

		# save paddles
		globals.waitlist_paddles = []
		for paddle in data['badges']:
			globals.waitlist_paddles.append(paddle)

		today_start_datetime = get_reset_datetime()
		today_swaps = 0

		# calculate the number of swaps made today
		# data is ordered from most recent to oldest
		for transaction in data['history']:
			transaction_datetime = string_to_datetime(transaction['createdAt'])

			if (transaction_datetime >= today_start_datetime):
				# add swap if it was completed today
				today_swaps = today_swaps + 1
			else:
				# swap is older, any data past this point is not needed
				break

		globals.waitlist_swaps = today_swaps