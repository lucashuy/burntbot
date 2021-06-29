import flask
import json

import globals

from api.labrie_check import labrie_check
from api.wallet import get_wallet
from api.users import search
from utilities.swap import swap as sswap
from utilities.datetime import string_to_datetime, get_reset_datetime

def check_swapped(shaketag):
	result = {
		'swapped': False,
		'do_swap': True
	}

	lower_shaketag = shaketag.lower()

	# oh no, an O(n) search
	for userid, history in globals.bot_history.items():
		if (history.get_shaketag() == lower_shaketag):
			reset_date = get_reset_datetime()
			last_swap_date = string_to_datetime(globals.bot_history[userid].get_timestamp())

			if (last_swap_date > reset_date):
				result['swapped'] = True

			result['last_date'] = last_swap_date.timestamp()

			break

	response = labrie_check(lower_shaketag, 'initiate')
	
	if (response['success']) and (not response['data']['allow_initiate']):
		result['do_swap'] = False
		result['reason'] = response['data']['reason'] or ''

	return json.dumps(result)

def swap(shaketag):
	data = flask.request.get_json()
	
	# check if amount field
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

	sswap(shaketag, amount, override = True, is_return = False, custom_note = note)
	
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