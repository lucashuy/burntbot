import flask
import threading
import logging
import click

import globals

from classes.bot import SwapBot

from routes.home import home_page
from routes.swap import swap, check_spelling, check_swapped
from routes.blacklist import blacklist_add, blacklist_delete, blacklist_page
from routes.settings import settings_page, settings_save
from routes.list import *

class WebUI(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.app = flask.Flask(__name__)
		self.app.template_folder = '../templates'
		self.app.static_folder = '../static'

		# disable logging if we dont have verbose
		if (not globals.bot_flags['verbose']):
			log = logging.getLogger('werkzeug')
			log.setLevel(logging.ERROR)
			
			def echo(text, file = None, nl = None, err = None, color = None, **styles): pass

			click.echo = echo
			click.secho = echo

	def _check_bot_state(self):
		request = flask.request

		if (request.endpoint == 'static'): return

		if (SwapBot.bot_state == 0) and (not request.endpoint == '_down_page'):
			# show down page if bot is down
			return flask.redirect(flask.url_for('_down_page'))
		elif (SwapBot.bot_state == 1) and (request.endpoint == '_down_page'):
			# redirect home if user goes to down page when bot is up
			return flask.redirect(flask.url_for('home_page'))

	def _down_page(self):
		return (flask.render_template('down.html'), 503)

	def run(self):
		self.app.add_url_rule('/down/', view_func = self._down_page)
		self.app.before_request(self._check_bot_state)

		self.app.add_url_rule('/', view_func = home_page)
		self.app.add_url_rule('/check/<string:shaketag>', view_func = check_swapped)
		self.app.add_url_rule('/search/<string:shaketag>', view_func = check_spelling)

		self.app.add_url_rule('/swap/<string:shaketag>', view_func = swap, methods = ['POST'])

		self.app.add_url_rule('/blacklist/', view_func = blacklist_page)
		self.app.add_url_rule('/blacklist/<string:shaketag>', view_func = blacklist_add, methods = ['POST'])
		self.app.add_url_rule('/blacklist/<string:shaketag>', view_func = blacklist_delete, methods = ['DELETE'])

		self.app.add_url_rule('/settings/', view_func = settings_page, methods = ['GET'])
		self.app.add_url_rule('/settings/', view_func = settings_save, methods = ['PATCH'])

		self.app.add_url_rule('/list/', view_func = list_page)
		self.app.add_url_rule('/list/', view_func = add_shaketags, methods = ['PATCH'])
		self.app.add_url_rule('/list/<string:shaketag>', view_func = delete_user, methods = ['DELETE'])
		self.app.add_url_rule('/list/clear/', view_func = clear_list, methods = ['DELETE'])
		self.app.add_url_rule('/list/send/', view_func = list_send)
		self.app.add_url_rule('/list/note/', view_func = change_note, methods = ['PATCH'])
		self.app.add_url_rule('/list/warning/<string:shaketag>', view_func = toggle_warning, methods = ['PATCH'])

		self.app.run(globals.webui_host, globals.webui_port, debug = False)