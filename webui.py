import flask
import threading
import json

import globals

from service.datetime import get_reset_datetime, string_to_datetime
from service.requests.version import is_even_version
from service.requests.waitlist import get_waitlist
from service.requests.users import search
from service.datetime import string_to_datetime, get_reset_datetime, get_paddle_datetime
from service.persistence import upsert_persistence

class WebUI(threading.Thread):
# class WebUI():
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.app = flask.Flask(__name__)

	def run(self):
		self.app.add_url_rule('/', view_func = self.home_route)
		self.app.add_url_rule('/check/<string:shaketag>', view_func = self.check_swapped)
		self.app.add_url_rule('/search/<string:shaketag>', view_func = self.check_spelling)
		self.app.add_url_rule('/blacklist/', view_func = self.balance_route)
		self.app.add_url_rule('/blacklist/<string:shaketag>', view_func = self.balance_add, methods = ['POST'])
		self.app.add_url_rule('/blacklist/<string:shaketag>', view_func = self.balance_delete, methods = ['DELETE'])

		self.app.run(globals.webui_host, globals.webui_port, debug = False)

	def home_route(self):
		get_waitlist()

		calc = self.get_stats()

		data = {
			'update': not is_even_version(),
			'shaketag': f'{globals.shaketag}',
			'unique': calc[1],
			'points_today': calc[0],
			'position': globals.waitlist_position,
			'points_total': globals.waitlist_points,
			'paddles': globals.waitlist_paddles
		}

		return flask.render_template('home.html', data = data)

	def balance_route(self):
		print(globals.blacklist)
		return flask.render_template('blacklist.html', data = globals.blacklist)

	def balance_add(self, shaketag):
		data = flask.request.get_json()
		
		amount = float(data['amount'])
		amount = amount * (-1 if data['direction'] == 'debit' else 1)

		if (data):
			globals.blacklist[shaketag] = amount

			upsert_persistence({'blacklist': globals.blacklist})

			return flask.Response(status = 201)
			
		return flask.Response(status = 400)

	def balance_delete(self, shaketag):
		if (shaketag in globals.blacklist):
			del globals.blacklist[shaketag]

			upsert_persistence({'blacklist': globals.blacklist})

			return flask.Response(status = 201)
			
		return flask.Response(status = 400)

	def get_stats(self) -> tuple:
		reset_datetime = get_reset_datetime()
		paddle_datetime = get_paddle_datetime()

		points_today = 0
		unique_swappers = 0

		for _, history in globals.history.items():
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
		for userid, history in globals.history.items():
			if (history.get_shaketag() == shaketag):
				reset_date = get_reset_datetime()
				last_swap_date = string_to_datetime(globals.history[userid].get_timestamp())

				if (last_swap_date > reset_date):
					result['swapped'] = True

				result['last_date'] = last_swap_date.timestamp()

				break

		return json.dumps(result)

	def swap(self, shaketag, note):
		pass

	def check_spelling(self, shaketag):
		usernames = search(shaketag)

		result = {
			'found': False
		}

		if (len(usernames) > 0):
			result['found'] = True
			result['match'] = usernames[0]

		return result