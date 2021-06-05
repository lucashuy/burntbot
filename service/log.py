import datetime

import globals

def log(msg: str, extra = False):
	if (extra) and (not globals.flags['verbose']): return

	formatted_datetime = datetime.datetime.now().strftime('[%Y%m%d %H:%M:%S]')

	print('{} {}'.format(formatted_datetime, msg))