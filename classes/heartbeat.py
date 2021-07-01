import threading
import time

import globals

from api.heart_beat import heart_beat

class HeartBeat(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)

	def run(self):
		while (globals.heart_beat_enabled and globals.bot_state):
			heart_beat()

			time.sleep(60 * 5)