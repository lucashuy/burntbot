import flask

import globals

from utilities.persistence import upsert_persistence
from utilities.datetime import get_reset_datetime, string_to_datetime
from utilities.swap import swap

from api.users import search
from api.labrie_check import labrie_check_multi
from api.wallet import get_wallet

def list_page():
	list_results = _classify_list()

	data = {
		'version': globals.version,
		'to_send': list_results['to_send'],
		'waiting': list_results['waiting'],
		'done': list_results['done'],
		'note': globals.list_note
	}

	return flask.render_template('list.html', data = data)

def add_shaketags():
	data = flask.request.get_json()
	
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

	upsert_persistence({'bot_send_list': globals.bot_send_list})

	return flask.Response(status = 201)

def delete_user(shaketag):
	if (shaketag in globals.bot_send_list): del globals.bot_send_list[shaketag]

	upsert_persistence({'bot_send_list': globals.bot_send_list})

	return flask.Response(status = 201)

def list_send():
	def _generate():
		try:
			to_send = _classify_list()['to_send']
			balance = _get_wallet_balance()

			for shaketag, data in to_send.items():
				if (balance < 5.): break

				if (not 'do_not_send' in data):
					swap(shaketag, 5.0, override = True, is_return = False, custom_note = globals.list_note)

					balance = balance - 5.

					yield f'data: {shaketag}\n\n'
		except: pass

		yield 'data: done\n\n'

	return flask.Response(_generate(), mimetype = 'text/event-stream')

def change_note():
	data = flask.request.get_json()

	globals.list_note = data['note'] or ''

	upsert_persistence({'list_note': globals.list_note})

	return flask.Response(status = 201)

def override_send(shaketag: str):
	balance = _get_wallet_balance()

	if (balance >= 5.):
		swap(shaketag, 5., True, False, globals.list_note)
		return flask.Response(status = 201)
	else:
		return flask.Response(status = 400)

# gets the amount of money we have minus swaps
def _get_wallet_balance() -> float:
	wallet = float(get_wallet()['balance'])

	for _, history in globals.bot_history.items():
		balance = history.get_swap()
		if (balance > 0): wallet = wallet - balance

	return wallet

def _generate_scammers_from_list() -> dict:
	send_list_array = []
	for shaketag in globals.bot_send_list:
		send_list_array.append(shaketag)

	# check names in database
	do_not_send = {}

	response = labrie_check_multi(send_list_array, 'initiate')

	if (response['success']):
		for data in response['data']:
			if (not data['allow_initiate']):
				do_not_send[f'@{data["shaketag"]}'] = data['reason']

	return do_not_send

def _username_history_cache() -> dict:
	usernames_local = {}
	# create local cache of usernames <-> user ids
	for userid, history in globals.bot_history.items():
		usernames_local[history.get_shaketag()] = userid

	return usernames_local

def _classify_list() -> dict:
	to_send = {}
	waiting = {}
	done = {}

	usernames_local = _username_history_cache()
	do_not_send = _generate_scammers_from_list()

	reset = get_reset_datetime()

	for shaketag in globals.bot_send_list:
		user_id = None
		user_history = None

		is_swap_today = True
		is_waiting = True

		try:
			user_id = usernames_local[shaketag]
			user_history = globals.bot_history[user_id]

			is_swap_today = string_to_datetime(user_history.get_timestamp()) > reset
			is_waiting = user_history.get_swap() < 0
		except KeyError: pass

		
		insert_obj = {}

		# check if we need to add ban message
		if (shaketag in do_not_send):
			insert_obj['do_not_send'] = do_not_send[shaketag]

		if (user_history == None) or (not is_swap_today and not is_waiting):
			to_send[shaketag] = insert_obj
		elif (is_waiting):
			insert_obj['timestamp'] = user_history.get_timestamp()
			waiting[shaketag] = insert_obj
		elif (is_swap_today and not is_waiting):
			done[shaketag] = insert_obj

	return {
		'to_send': to_send,
		'waiting': waiting,
		'done': done
	}