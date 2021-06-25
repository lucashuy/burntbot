import flask
import threading
import json

import globals

from service.datetime import get_reset_datetime, string_to_datetime
from service.requests.version import is_even_version
from service.requests.waitlist import get_waitlist
from service.requests.users import search
from service.requests.wallet import get_wallet
from service.swap import swap
from service.datetime import string_to_datetime, get_reset_datetime, get_paddle_datetime
from service.persistence import upsert_persistence

def add_commas(amount):
	int_rep = int(amount)

	if (int_rep > 9999):
		return f'{int_rep:,}'
	else:
		return int_rep

class WebUI(threading.Thread):
# class WebUI():
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.app = flask.Flask(__name__)
		self.app.template_folder = '../templates'
		self.app.static_folder = '../static'

		self.version = globals.version

	def run(self):
		self.app.add_url_rule('/', view_func = self.home_page)
		self.app.add_url_rule('/check/<string:shaketag>', view_func = self.check_swapped)
		self.app.add_url_rule('/search/<string:shaketag>', view_func = self.check_spelling)
		self.app.add_url_rule('/swap/<string:shaketag>', view_func = self.swap, methods = ['POST'])
		self.app.add_url_rule('/blacklist/', view_func = self.blacklist_page)
		self.app.add_url_rule('/blacklist/<string:shaketag>', view_func = self.blacklist_add, methods = ['POST'])
		self.app.add_url_rule('/blacklist/<string:shaketag>', view_func = self.blacklist_delete, methods = ['DELETE'])
		self.app.add_url_rule('/settings/', view_func = self.settings_page, methods = ['GET'])
		self.app.add_url_rule('/settings/', view_func = self.settings_save, methods = ['PATCH'])

		self.app.run(globals.webui_host, globals.webui_port, debug = False)

	def home_page(self):
		get_waitlist()

		stats_calc = self.get_stats()
		owe_calc = self.determine_balances()

		data = {
			'update': not is_even_version(),
			'version': self.version,
			'shaketag': f'{globals.shaketag}',
			'unique': add_commas(stats_calc[1]),
			'points_today': add_commas(stats_calc[0]),
			'position': add_commas(globals.waitlist_position),
			'points_total': add_commas(globals.waitlist_points),
			'paddles': globals.waitlist_paddles,
			'they_owe': owe_calc[0],
			'we_owe': owe_calc[1],
		}

		return flask.render_template('home.html', data = data)

	def settings_page(self):
		data = {
			'version': self.version,
			'poll_rate': globals.bot_poll_rate,
			'note': globals.bot_note
		}

		return flask.render_template('settings.html', data = data)

	def settings_save(self):
		save_data = {}
		data = flask.request.get_json()

		# dont know if this is the right choice for validation:
		# i am only checking for certain keys and saving those while ignoring the rest

		if ('note' in data):
			save_data['note'] = data['note']
			globals.bot_note = data['note']

		# also make sure poll rate doesnt break API rate limit
		if ('poll_rate' in data):
			cast_poll_rate = float(data['poll_rate'])

			if (cast_poll_rate < 4):
				flask.Response(status = 400)
			else:
				save_data['poll_rate'] = cast_poll_rate
				globals.bot_poll_rate = cast_poll_rate

		if ('return_check' in data):
			save_data['bot_return_check'] = data['return_check']
			globals.bot_return_check = data['return_check']

		upsert_persistence(save_data)
		
		return flask.Response(status = 201)

	def determine_balances(self) -> dict:
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

	def blacklist_page(self):
		data = {
			'version': self.version,
			'blacklist': globals.bot_blacklist
		}

		return flask.render_template('blacklist.html', data = data)

	def blacklist_add(self, shaketag):
		data = flask.request.get_json()
		
		amount = float(data['amount'])
		amount = amount * (1 if data['direction'] == 'debit' else -1)

		if (data):
			globals.bot_blacklist[shaketag] = amount

			upsert_persistence({'blacklist': globals.bot_blacklist})

			return flask.Response(status = 201)
			
		return flask.Response(status = 400)

	def blacklist_delete(self, shaketag):
		if (shaketag in globals.bot_blacklist):
			del globals.bot_blacklist[shaketag]

			upsert_persistence({'blacklist': globals.bot_blacklist})

			return flask.Response(status = 201)
			
		return flask.Response(status = 400)

	def get_stats(self) -> tuple:
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

	def check_swapped(self, shaketag):
		result = {
			'swapped': False
		}

		# oh no, an O(n) search
		for userid, history in globals.bot_history.items():
			if (history.get_shaketag() == shaketag):
				reset_date = get_reset_datetime()
				last_swap_date = string_to_datetime(globals.bot_history[userid].get_timestamp())

				if (last_swap_date > reset_date):
					result['swapped'] = True

				result['last_date'] = last_swap_date.timestamp()

				break

		return json.dumps(result)

	def swap(self, shaketag):
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

		swap(shaketag, amount, override = True, is_return = False, custom_note = note)
		
		return flask.Response(status = 201)

	def check_spelling(self, shaketag):
		usernames = search(shaketag)

		result = {
			'found': False
		}

		if (len(usernames) > 0):
			result['found'] = True
			result['match'] = usernames[0]

		return result