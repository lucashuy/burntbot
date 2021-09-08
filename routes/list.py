import flask
import time
import hashlib

import globals

from utilities.swap import swap
from api.users import search
from api.labrie_check import labrie_check_multi, labrie_check
from api.wallet import get_wallet
from classes.sqlite import SQLite

def list_page():
	db = SQLite()

	list_results = _classify_list()

	data = {
		'version': globals.version,
		'not_sent': list_results[0],
		'wait_returns': list_results[1],
		'done_swap': list_results[2],
		'note': db.get_key_value('list_note', '')
	}

	db.close()

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
				if (globals.bot_state == 0): break

				# ignore send if we ignored them in UI
				if ('delay_state' in data) and (data['delay_time'] > int(time.time())): continue

				# only send if they are not marked in the database
				if ('do_not_send' in data) and (not 'warning_hash' in data): continue

				# if we ran out of money, check again to see if bot got any swaps back
				if (balance < 5.):
					balance = _get_wallet_balance()
					
					# if we still dont have enough money, stop
					if (balance < 5.): break

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

def clear_list():
	globals.bot_send_list = {}

	upsert_persistence({'bot_send_list': {}})

	return flask.Response(status = 201)

def toggle_warning(shaketag: str):
	if ('warning_hash' in globals.bot_send_list[shaketag]):
		del globals.bot_send_list[shaketag]['warning_hash']
	else:
		response = labrie_check(shaketag, 'initiate')['data']
		globals.bot_send_list[shaketag]['warning_hash'] = _make_hash(response['added_time'], response['reason'])
		
	upsert_persistence({'bot_send_list': globals.bot_send_list})

	return flask.Response(status = 201)

def _make_hash(time: str, reason: str) -> str:
	'''
	Helper function to turn reason + datetime string from swapper database into a hash

	@param `time` A datetime string
	@param `reason` The reason for the warning

	@returns The `md5` hashed string
	'''
	return hashlib.md5(f'{time}{reason}'.encode('utf-8')).hexdigest()

def _get_wallet_balance() -> float:
	'''
	Returns the balance we have available for initiating swaps

	@returns The balance we have for initiating
	'''

	wallet = float(get_wallet()['balance'])

	for _, history in globals.bot_history.items():
		balance = history.get_swap()
		if (balance > 0): wallet = wallet - balance

	return wallet

def _classify_list() -> tuple:
	'''
	Helper function to separate those that we've swapped with, are waiting for funds, and haven't swapped yet

	@returns `tuple` in the format `(not_sent: list, wait_returns: list, done_swap: list)`
	'''

	not_sent = []
	wait_returns = []
	done_swap = []

	# used to check for notices
	not_sent_dict = {}

	db = SQLite()

	# get the list from the DB and initialize debits list (the people we are waiting for)
	send_list = db.get_list()
	debits = {}

	# turn the array of tuples into a dictionary
	for row in db.get_debits():
		debits[row[0]] = {
			'amount': row[1],
			'timestamp': row[2]
		}

	for user in send_list:
		shaketag = user[0]

		if (shaketag in debits):
			# add to waiting list if we are waiting for a return
			wait_returns.append(user)
		else:
			# check list and separate those that we havent and have swapped
			if (db.have_swapped(shaketag)):
				done_swap.append(user)
			else:
				# we have not swapped with this user yet
				not_sent_dict[shaketag] = user

	# check if anyone from the send list has warnings and save the result as a list of values
	not_sent = [*_check_warnings(not_sent_dict, db).values()]

	db.commit()
	db.close()

	return (not_sent, wait_returns, done_swap)

def _check_warnings(list: dict, db: SQLite) -> dict:
	'''
	Helper function to check swapper database for warnings

	@param `list` A dictionary of shaketags and rows from database
	@param `check_list` A list of shaketags to check

	@returns A dictonary of rows formatted like the `list` table in the database
	'''

	not_sent = list.copy()

	# save the shaketags as a list
	check_list = [*not_sent.keys()]

	# check the not sent list for scammers
	results = []
	
	# skip asking API for info on empty send list
	if (not len(check_list) == 0):
		results = labrie_check_multi(check_list, 'initiate')
		results = results['data'] if results['success'] else []

	# update our not sent list with notice data
	for notice in results:
		shaketag = f'@{notice["shaketag"]}'
		list_user = not_sent[shaketag]

		# create hash of reason and datetime string
		warning_hash = _make_hash(notice['reason'], notice['added_time'])

		# used to create new tuple
		updated_warning = list_user[2]

		if (not list_user[2] == None) and (not list_user[2] == warning_hash):
			# the warning we ignored from before is different, remove it from DB and from list
			db.update_list_warning(shaketag, None)
			updated_warning = None

		if (not notice['allow_initiate']):
			# add the reason for notice to warning
			updated_warning = notice['reason']

		# update warning
		not_sent[shaketag] = (list_user[0], list_user[1], updated_warning)

	return not_sent