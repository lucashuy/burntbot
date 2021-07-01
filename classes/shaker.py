import threading
import time

import globals

from api.shakingsats import shaking_sats

class ShakingSats(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)

	def run(self):
		while (globals.shaking_sats_enabled and globals.bot_state):
			shaking_sats()

			# 12 hour cooldown between shakes
			time.sleep(60 * 60 * 12)