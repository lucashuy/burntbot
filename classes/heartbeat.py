import threading

import globals

from api.heart_beat import heart_beat

class HeartBeat(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.stop = threading.Event()

	def run(self):
		while (not self.stop.is_set()) and (globals.heart_beat_enabled) and (globals.bot_state) and (not globals.bot_flags['listen']):
			heart_beat()

			self.stop.wait(60 * 5)