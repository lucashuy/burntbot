import flask
import threading

class WebUI(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.app = flask.Flask(__name__)

	def run(self):
		self.app.add_url_rule('/', '', self.home)

		self.app.run(debug = False)

	def home(self):
		swappers = ['name1', 'name2', 'name3']

		return flask.render_template('layout.html', swappers = swappers)
