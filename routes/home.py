import flask

import globals

from api.waitlist import update_waitlist
from api.version import get_master_version
from classes.sqlite import SQLite
from utilities.demo_data import demo_paddle_data

def home_page():
	db = SQLite()

	they_owe = []
	we_owe = []
	unique_swappers = 0

	if (globals.bot_flags['demo'] == False):
		they_owe = db.get_debits()
		we_owe = db.get_credits()
		unique_swappers = _add_commas(db.get_paddle_swappers())

		update_waitlist()
	else:
		# fake waitlist details
		globals.shaketag = '@demonstration'
		globals.waitlist_swaps = 87
		globals.waitlist_position = 30
		globals.waitlist_points = 1185205
		globals.waitlist_paddles = demo_paddle_data
		unique_swappers = 543

		they_owe = [('@kramer', 5.0)]

	master_version = get_master_version()

	data = {
		'update': master_version > globals.version,
		'master_version': master_version,
		'version': globals.version,
		'shaketag': f'{globals.shaketag}',
		'unique': unique_swappers,
		'points_today': _add_commas(int(globals.waitlist_swaps) * 69),
		'position': _add_commas(globals.waitlist_position),
		'points_total': _add_commas(globals.waitlist_points),
		'paddles': globals.waitlist_paddles,
		'they_owe': they_owe,
		'we_owe': we_owe,
	}

	db.close()

	return flask.render_template('home.html', data = data)

def _add_commas(amount: float) -> str:
	'''
	Helper function to add commas to large numbers.\n
	`9999` stays as `9999`\n
	`10000` becomes `10,000`

	@param `amount` The amount to add commas to

	@returns A string with commas in it
	'''
	
	int_rep = int(amount)

	if (int_rep > 9999):
		return f'{int_rep:,}'
	else:
		return int_rep