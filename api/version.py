import requests

import globals

from classes.version import Version
from utilities.log import log

def get_master_version() -> bool:
	response = requests.get('https://raw.githubusercontent.com/itslupus/burntbot/master/.version')

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when fetching version')
		
		# return current version if something goes wrong so that we dont display notification
		return globals.version

	return Version(response.text.strip())
