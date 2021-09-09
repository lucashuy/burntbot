import flask
import time
import hashlib

import globals

from utilities.swap import swap
from api.users import search
from api.labrie_check import labrie_check_multi, labrie_check
from api.wallet import get_wallet
from classes.sqlite import SQLite
from classes.bot import SwapBot

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
	'''
	Route to add shaketag to list. API returns 201 if nothing crashes.
	'''
	
	db = SQLite()

	data = flask.request.get_json()
	
	for shaketag in data['shaketags']:
		formatted_tag = shaketag.strip()

		if (formatted_tag == ''): continue

		# append @ before
		if (formatted_tag[0] != '@'): formatted_tag = f'@{formatted_tag}'

		# check valid chars
		if (not formatted_tag[1:].isalnum()): continue

		# check if the shaketag is valid (by pinging shakepay)
		results = search(formatted_tag)

		if (len(results) == 1) and (results[0] == formatted_tag): db.add_list(formatted_tag)

	db.commit()
	db.close()

	return flask.Response(status = 201)

def delete_user(shaketag):
	'''
	Removes a shaketag from the list. API returns 201 if nothing crashes.
	'''
	
	db = SQLite()
	db.delete_from_list(shaketag)
	db.commit()
	db.close()
	
	return flask.Response(status = 201)

def list_send():
	'''
	Route to automatically send to the list. Uses eventstreams to send data to the client to move `div`s to other columns
	'''

	db = SQLite()
	note = db.get_key_value('list_note', '')
	db.close()

	# generator function for event stream
	def _generate():
		try:
			# get not sent list and current wallet balance
			to_send = _classify_list()[0]
			balance = _get_wallet_balance()

			for data in to_send:
				if (SwapBot.bot_state == 0): break

				shaketag = data[0]

				# only send if they are not marked in the database
				# if data has 4 children, this means we are currently ignoring them, send
				# if data has 3 children and the warning (3rd child) is NOT None, dont send
				num_children = len(data)
				if (num_children == 3) and (not data[2] == None): continue

				# if we ran out of money, check again to see if bot got any swaps back
				if (balance < 5.):
					balance = _get_wallet_balance()
					
					# if we still dont have enough money, stop
					if (balance < 5.): break

				swap(shaketag, 5., note, False, True, False)

				balance = balance - 5.

				# send shaketag to client
				yield f'data: {shaketag}\n\n'
		except: pass

		# kill client
		yield 'data: done\n\n'

	return flask.Response(_generate(), mimetype = 'text/event-stream')

def change_note():
	'''
	Route to change the list's note
	'''
	
	data = flask.request.get_json()

	db = SQLite()
	db.upsert_key_value('list_note', data['note'] or '')
	db.commit()
	db.close()

	return flask.Response(status = 201)

def clear_list():
	'''
	Route to delete the entire list
	'''

	db = SQLite()
	db.clear_list()
	db.commit()
	db.close()
	
	return flask.Response(status = 201)

def toggle_warning(shaketag: str):
	'''
	Route to toggle the ignoring of database warnings
	'''
	
	db = SQLite()
	user = db.get_list_shaketag(shaketag)

	if (user):
		ignored_warning = user[2]

		if (ignored_warning == None):
			# add warning
			response = labrie_check(shaketag, 'initiate')['data']
			ignored_warning = _make_hash(response['added_time'], response['reason'])
		else:
			# remove warning
			ignored_warning = None

		db.update_list_warning(shaketag, ignored_warning)

	db.commit()
	db.close()

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

	balance = float(get_wallet()['balance'])

	db = SQLite()

	for data in db.get_credits():
		balance = balance - data[1]

	db.close()

	return balance

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

	# save the shaketags as a list for swapper DB check
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
		warning_hash = _make_hash(notice['added_time'], notice['reason'])

		# used to create new tuple
		updated_warning = list_user[2]

		ignore_warning = False

		if (not list_user[2] == None):
			if (not list_user[2] == warning_hash):
				# the warning we ignored from before is different, remove it from DB and from list
				db.update_list_warning(shaketag, None)
				updated_warning = None
			else:
				# the warning is the same, this means we should ignore sending
				ignore_warning = True

		if (not notice['allow_initiate']):
			# change 3rd element to the reason
			updated_warning = notice['reason']

		# update the tuple
		if (ignore_warning):
			not_sent[shaketag] = (list_user[0], list_user[1], updated_warning, True)
		else:
			not_sent[shaketag] = (list_user[0], list_user[1], updated_warning)

	return not_sent