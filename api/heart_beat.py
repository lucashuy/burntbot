import requests

import globals

from api.waitlist import update_waitlist
from utilities.datetime import get_reset_datetime, string_to_datetime

def heart_beat():
	fetched_waitlist = False
	metadata = {}

	data =  {
		'guid': globals.headers['X-Device-Unique-Id'],
		'shaketag': globals.shaketag,
	}

	if (globals.heart_beat_points):
		# fetch any new data
		if (not fetched_waitlist):
			update_waitlist()
			fetched_waitlist = True

		metadata["points"] = globals.waitlist_points

	if (globals.heart_beat_swaps):
		# fetch any new data
		if (not fetched_waitlist):
			update_waitlist()
			fetched_waitlist = True

		metadata["swapsToday"] = _count_swaps_today()

	if (globals.heart_beat_position):
		# fetch any new data
		if (not fetched_waitlist):
			update_waitlist()
			fetched_waitlist = True

		metadata["position"] = globals.waitlist_position

	if (len(metadata) > 0):
		data['metadata'] = metadata

	requests.post('https://swap.labrie.ca/api/ping/', json = data)

def _count_swaps_today() -> int:
	swaps_today = 0
	reset = get_reset_datetime()

	for _, history in globals.bot_history.items():
		if (string_to_datetime(history.get_timestamp()) > reset):
			swaps_today = swaps_today + 1

	return swaps_today