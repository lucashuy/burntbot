import requests

import globals

from utilities.log import log
from classes.sqlite import SQLite
from utilities.persistence import read_persistence

def migrate():
	db = SQLite()
	version = db.get_key_value('version')

	if (version == None):
		log('Migrate to 0.9.0', True)

		db.upsert_key_value('version', '0.9.0')

		try:
			old_persistence = read_persistence()

			# =====================
			# migrate blacklists
			#
			for shaketag, amount in old_persistence['blacklist'].items():
				db.upsert_blacklist(shaketag, amount)

			# =====================
			# migrate kv pairs
			#
			db.upsert_key_value('poll_rate', old_persistence['poll_rate'])
			db.upsert_key_value('return_note', old_persistence['note'])
			db.upsert_key_value('bot_return_check', old_persistence['bot_return_check'])
			db.upsert_key_value('shaking_sats', old_persistence['shaking_sats_enabled'])
			db.upsert_key_value('list_note', old_persistence['list_note'])

			# determine if we should enable the heart beat based on new requirements
			if (old_persistence['heart_beat'] and old_persistence['heart_beat_swaps'] and old_persistence['heart_beat_points'] and old_persistence['heart_beat_position']):
				db.upsert_key_value('heart_beat', True)
			else:
				db.upsert_key_value('heart_beat', False)

			# =====================
			# migrate send list
			#
			for shaketag in old_persistence['bot_send_list']:
				db.add_list(shaketag)

			# log user out since going forward we no longer use serial number
			local_headers = globals.headers.copy()
			local_headers['Authorization'] = old_persistence['token']
			local_headers['X-Device-Unique-Id'] = old_persistence['unique_id']
			local_headers['X-Device-Serial-Number'] = old_persistence['serial_number']

			requests.delete('https://api.shakepay.com/authentication?allSessions=false', headers = local_headers)
		except: pass

		db.commit()

	db.close()