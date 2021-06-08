import requests

import globals

from service.requests.exception import raise_exception
from service.log import log

def get_waitlist():
	local_headers = globals.headers.copy()
	if (globals.waitlist_etag): local_headers['If-None-Match'] = globals.waitlist_etag

	response = requests.get(globals.endpoint_waitlist, headers = local_headers)

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