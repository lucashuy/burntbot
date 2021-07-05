import flask

import globals

from utilities.persistence import upsert_persistence
from utilities.datetime import get_reset_datetime, string_to_datetime
from api.users import search

def list_page():
	list_results = _classify_list()

	data = {
		'version': globals.version,
		'to_send': list_results['to_send'],
		'waiting': list_results['waiting'],
		'done': list_results['done']
	}

	return flask.render_template('list.html', data = data)

def add_shaketags():
	data = flask.request.get_json()
	
	print(data)

	for shaketag in data['shaketags']:
		local_tag = shaketag.strip()

		if (local_tag == ''): continue

		# append @ before
		if (local_tag[0] != '@'): local_tag = f'@{local_tag}'

		# check valid chars
		if (not local_tag[1:].isalnum()): continue

		# check if the shaketag is valid (by pinging shakepay)
		results = search(local_tag)

		if (len(results) == 1) and (results[0] == local_tag):
			globals.bot_send_list[local_tag] = 1

	print(globals.bot_send_list)

	upsert_persistence({'bot_send_list': globals.bot_send_list})

	return flask.Response(status = 201)

def _classify_list() -> dict:
	to_send = {}
	waiting = {}
	done = {}

	usernames_local = {}
	# create local cache of usernames <-> user ids
	for userid, history in globals.bot_history.items():
		usernames_local[history.get_shaketag()] = userid

	reset = get_reset_datetime()

	for shaketag in globals.bot_send_list:
		user_id = None
		user_history = None

		try:
			user_id = usernames_local[shaketag]
			user_history = globals.bot_history[user_id]
		except KeyError: pass

		is_swap_today = string_to_datetime(user_history.get_timestamp()) > reset
		is_waiting = user_history.get_swap() < 0
		print(f'{shaketag} {is_swap_today} {is_waiting}')
		if (user_history == None) or (not is_swap_today and not is_waiting):
			to_send[shaketag] = 1
		elif (is_waiting):
			waiting[shaketag] = 1
		elif (is_swap_today and not is_waiting):
			done[shaketag] = 1

	return {
		'to_send': to_send,
		'waiting': waiting,
		'done': done
	}