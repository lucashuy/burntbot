import flask
import threading
import json

import logic_service
import globals

# class WebUI(threading.Thread):
class WebUI():
	def __init__(self):
		# threading.Thread.__init__(self, daemon = True)
		self.app = flask.Flask(__name__)

	def run(self):
		self.app.add_url_rule('/', view_func = self.home)
		self.app.add_url_rule('/check/<string:shaketag>', view_func = self.check_swapped)

		self.app.run(debug = True)

	def home(self):
		return flask.render_template('layout.html')

	def check_swapped(self, shaketag):
		result = {
			'exists': False,
			'swapped': False
		}

		if (shaketag in globals.history):
			result['exists'] = True

			reset_date = logic_service.get_reset_datetime()
			last_swap_date = logic_service.string_to_datetime(globals.history['shaketag']['timestamp'])

			if (last_swap_date > reset_date):
				result['swapped'] = True

		return json.dumps(result)