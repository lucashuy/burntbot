import flask

import globals

from utilities.persistence import upsert_persistence

def blacklist_page():
	they_sent = []
	we_sent = []

	for user, amount in globals.bot_blacklist.items():
		insert = {'shaketag': user, 'amount': f'${abs(amount):.2f}'}

		if (amount > 0):
			they_sent.append(insert)
		else:
			we_sent.append(insert)

	data = {
		'version': globals.version,
		'they_sent': they_sent,
		'we_sent': we_sent
	}

	print(data)

	return flask.render_template('blacklist.html', data = data)

def blacklist_add(shaketag):
	data = flask.request.get_json()
	
	amount = float(data['amount'])
	amount = amount * (1 if data['direction'] == 'debit' else -1)

	if (data):
		globals.bot_blacklist[shaketag.lower()] = amount

		upsert_persistence({'blacklist': globals.bot_blacklist})

		return flask.Response(status = 201)
		
	return flask.Response(status = 400)

def blacklist_delete(shaketag):
	if (shaketag in globals.bot_blacklist):
		del globals.bot_blacklist[shaketag]

		upsert_persistence({'blacklist': globals.bot_blacklist})

		return flask.Response(status = 201)
		
	return flask.Response(status = 400)