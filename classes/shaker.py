import threading

import globals

from api.shakingsats import shaking_sats

class ShakingSats(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.stop = threading.Event()

	def run(self):
		while (not self.stop.is_set()) and (globals.shaking_sats_enabled and globals.bot_state):
			shaking_sats()

			# 8 hour cooldown between shakes
			self.stop.wait(60 * 60 * 8)