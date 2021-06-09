import requests

import globals

from service.log import log

def is_even_version() -> bool:
	response = requests.get('https://raw.githubusercontent.com/itslupus/swappong/master/.version')

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching version')
		
		# return true if something goes wrong so that we dont display notification
		return True

	master_version = response.text.strip()
	return master_version == globals.version