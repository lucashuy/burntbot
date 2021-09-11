import flask
import json

from api.labrie_check import labrie_check
from api.wallet import get_wallet
from api.users import search
from utilities.swap import swap
from utilities.datetime import get_reset_datetime
from classes.sqlite import SQLite

def check_swapped(shaketag):
	'''
	Checks if we have swapped with the user today
	'''
	
	db = SQLite()

	lowercase_shaketag = shaketag.lower()
	today_start_timestamp = get_reset_datetime().timestamp()
	
	user_info = db.get_shaketag_info(lowercase_shaketag)

	return_data = {'state': 'NOT_SWAPPED'}
	if (user_info == None):
		# potential new swap
		return_data = {'state': 'NEW_USER'}
	else:
		timestamp = user_info[2]

		if (timestamp >= today_start_timestamp):
			# check if we have actually swapped today, or if it was just a return
			did_swap = db.have_swapped(lowercase_shaketag)

			if (did_swap):
				# we returned today
				return_data = {'state': 'SWAPPED'}
	
	# check scammer db
	response = labrie_check(lowercase_shaketag, 'initiate')
	
	# set state to reason from database if they are marked
	if (response['success']) and (not response['data']['allow_initiate']):
		return_data['state'] = response['data']['reason'] or ''

	db.close()

	return json.dumps(return_data)

def send_transaction(shaketag):
	data = flask.request.get_json()
	
	# check if amount field is valid
	if (data['amount'] == None) or (data['amount'] == ''): return flask.Response(status = 400)

	# add @ to start and make it lowercase
	local_shaketag = shaketag.lower()
	if (local_shaketag[0] != '@'): local_shaketag = f'@{local_shaketag}'

	amount = float(data['amount'])

	# check for valid amount to send
	if (amount <= 0): return flask.Response(status = 400)

	# make sure we actually have enough money to send :/
	if (get_wallet()['balance'] < amount): return flask.Response(status = 400)

	note = data['note'] or ''

	swap(shaketag, amount, note, False, override = True, is_return = False)
	
	return flask.Response(status = 201)

def check_spelling(shaketag):
	usernames = search(shaketag)

	result = {
		'found': False
	}

	if (len(usernames) > 0):
		result['found'] = True
		result['match'] = usernames[0]

	return result