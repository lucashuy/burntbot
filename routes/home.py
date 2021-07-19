import flask

import globals

from api.waitlist import get_waitlist
from api.version import get_master_version
from utilities.datetime import get_reset_datetime, string_to_datetime, get_paddle_datetime

def home_page():
	get_waitlist()

	stats_calc = _get_stats()
	owe_calc = _determine_balances()

	master_version = get_master_version()

	data = {
		'update': master_version > globals.version,
		'master_version': master_version,
		'version': globals.version,
		'shaketag': f'{globals.shaketag}',
		'unique': _add_commas(stats_calc[1]),
		'points_today': _add_commas(stats_calc[0]),
		'position': _add_commas(globals.waitlist_position),
		'points_total': _add_commas(globals.waitlist_points),
		'paddles': globals.waitlist_paddles,
		'they_owe': owe_calc[0],
		'we_owe': owe_calc[1],
	}

	return flask.render_template('home.html', data = data)

def _add_commas(amount: float) -> str:
	int_rep = int(amount)

	if (int_rep > 9999):
		return f'{int_rep:,}'
	else:
		return int_rep


def _get_stats() -> tuple:
	reset_datetime = get_reset_datetime()
	paddle_datetime = get_paddle_datetime()

	points_today = 0
	unique_swappers = 0

	for _, history in globals.bot_history.items():
		last_swap = string_to_datetime(history.get_timestamp())

		# add to today points
		if (last_swap >= reset_datetime): points_today = points_today + 69

		# add unique swappers
		if (last_swap >= paddle_datetime): unique_swappers = unique_swappers + 1

	return points_today, unique_swappers


def _determine_balances() -> dict:
	they = []
	we = []

	for _, history in globals.bot_history.items():
		swap = history.get_swap()

		if (swap != 0.):
			obj = {
				'shaketag': history.get_shaketag(),
				'amount': f'${abs(swap):.2f}',
				'timestamp': history.get_timestamp()
			}

			if (swap > 0):
				we.append(obj)
			else:
				they.append(obj)

	return (they, we)