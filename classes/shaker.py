import threading

from api.shakingsats import shaking_sats
from classes.sqlite import SQLite
from classes.bot import SwapBot

class ShakingSats(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.stop = threading.Event()

	def run(self):
		db = SQLite()

		while (not self.stop.is_set()) and (db.get_key_value('shaking-sats'), False) and (SwapBot.bot_state):
			shaking_sats()

			# 8 hour cooldown between shakes
			self.stop.wait(60 * 60 * 8)

		db.close()