import datetime

def log(msg: str):
	formatted_datetime = datetime.datetime.now().strftime('[%Y%m%d %H:%M:%S]')

	print('{} {}'.format(formatted_datetime, msg))