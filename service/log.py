import datetime

import globals

def log(msg: str, extra = False):
	if (extra) and (not globals.bot_flags['verbose']): return

	formatted_datetime = datetime.datetime.now().strftime('[%Y%m%d %H:%M:%S]')

	print('{} {}'.format(formatted_datetime, msg))