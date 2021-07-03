import flask

import globals

def list_page():
	data = {
		'version': globals.version
	}

	return flask.render_template('list.html', data = data)