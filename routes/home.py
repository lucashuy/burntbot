import flask

import globals

from api.waitlist import update_waitlist
from api.version import get_master_version
from classes.sqlite import SQLite

def home_page():
	db = SQLite()

	update_waitlist()

	master_version = get_master_version()

	data = {
		'update': master_version > globals.version,
		'master_version': master_version,
		'version': globals.version,
		'shaketag': f'{globals.shaketag}',
		'unique': _add_commas(db.get_paddle_swappers()),
		'points_today': _add_commas(int(globals.waitlist_swaps) * 69),
		'position': _add_commas(globals.waitlist_position),
		'points_total': _add_commas(globals.waitlist_points),
		'paddles': globals.waitlist_paddles,
		'they_owe': db.get_debits(),
		'we_owe': db.get_credits(),
	}

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