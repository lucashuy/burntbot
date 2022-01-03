import flask
import time

import globals

from classes.sqlite import SQLite

def settings_page():
	'''
	Route function
	'''

	db = SQLite()

	data = {
		'version': globals.version,
		'poll_rate': db.get_key_value('poll_rate', 10),
		'note': db.get_key_value('return_note', ''),
		'return_check': db.get_key_value('bot_return_check', False),
		'shaking_sats_enabled': db.get_key_value('shaking_sats', False),
		'heart_beat': db.get_key_value('heart_beat', False)
	}

	db.close()

	return flask.render_template('settings.html', data = data)

def settings_save():
	'''
	Route to save settings
	'''

	if (globals.bot_flags['demo'] == True):
		time.sleep(1)
		return flask.Response(status = 201)

	db = SQLite()

	data = flask.request.get_json()
	status_code = 201

	if ('note' in data): db.upsert_key_value('return_note', data['note'])
	if ('return_check' in data): db.upsert_key_value('bot_return_check', data['return_check'])
	if ('shaking_sats_enabled' in data): db.upsert_key_value('shaking_sats', data['shaking_sats_enabled'])
	if ('heart_beat' in data): db.upsert_key_value('heart_beat', data['heart_beat'])

	# make sure poll rate does not spam API
	if ('poll_rate' in data):
		poll_rate = float(data['poll_rate'])

		if (poll_rate < 1):
			status_code = 400
		else:
			# save poll rate
			db.upsert_key_value('poll_rate', poll_rate)

	db.commit()
	db.close()

	return flask.Response(status = status_code)