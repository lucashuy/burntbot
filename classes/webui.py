import flask
import threading

import globals

from routes.home import home_page
from routes.swap import swap, check_spelling, check_swapped
from routes.blacklist import blacklist_add, blacklist_delete, blacklist_page
from routes.settings import settings_page, settings_save
from routes.list import list_page, add_shaketags, delete_user, list_send, change_note, override_send

class WebUI(threading.Thread):
# class WebUI():
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.app = flask.Flask(__name__)
		self.app.template_folder = '../templates'
		self.app.static_folder = '../static'

	def run(self):
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
		self.app.add_url_rule('/list/send/', view_func = list_send)
		self.app.add_url_rule('/list/send/<string:shaketag>', view_func = override_send, methods = ['POST'])
		self.app.add_url_rule('/list/note/', view_func = change_note, methods = ['PATCH'])

		self.app.run(globals.webui_host, globals.webui_port, debug = False)