import threading

import globals

from api.heart_beat import heart_beat
from classes.sqlite import SQLite
from classes.bot import SwapBot

class HeartBeat(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, daemon = True)
		self.stop = threading.Event()

	def run(self):
		db = SQLite()

		while (not self.stop.is_set()) and (db.get_key_value('heart_beat', False)) and (SwapBot.bot_state) and (not globals.bot_flags['listen']):
			heart_beat()

			# ping swapper database every 45 seconds
			self.stop.wait(45)

		db.close()