import flask
import time

import globals

from classes.sqlite import SQLite

def blacklist_page():
	'''
	Route for blacklist web UI page
	'''

	db = SQLite()

	they_sent = []
	we_sent = []

	if (globals.bot_flags['demo'] == False):
		# separate the ones that sent and the ones we sent
		for blacklist in db.get_blacklist():
			insert = {'shaketag': blacklist[0], 'amount': blacklist[1]}

			if (blacklist[1] > 0):
				they_sent.append(insert)
			else:
				we_sent.append(insert)
	else:
		they_sent = [{'shaketag': '@unclejimmy', 'amount': '25.49'}]
		we_sent = [{'shaketag': '@gasmoney', 'amount': '-10.00'}]

	data = {
		'version': globals.version,
		'they_sent': they_sent,
		'we_sent': we_sent
	}

	return flask.render_template('blacklist.html', data = data)

def blacklist_add(shaketag):
	'''
	Route to add a shaketag to blacklist with amount
	'''

	data = flask.request.get_json()
	
	# determine which way to blacklist
	# if they sent to us, make it negative
	# this way when the bot tallies up balances, they will have a balance of +x (meaning we need to return)
	# so the blacklist is then negated and added onto the balance, making it 0.00
	amount = float(data['amount'])
	amount = amount * (1 if data['direction'] == 'debit' else -1)

	status_code = 400

	db = SQLite()

	if (data):
		db.upsert_blacklist(shaketag.lower(), amount)
		db.commit()

	if (data) or (globals.bot_flags['demo'] == True):
		status_code = 201

	db.close()

	return flask.Response(status = status_code)

def blacklist_delete(shaketag):
	'''
	Route to remove shaketag from blacklist, will not error out if shaketag does not exist
	'''
	
	if (globals.bot_flags['demo'] == True):
		time.sleep(1.5)
		return flask.Response(status = 201)

	db = SQLite()
	db.delete_blacklist(shaketag.lower())
	db.commit()
	db.close()
		
	return flask.Response(status = 201)