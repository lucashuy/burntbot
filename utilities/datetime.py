import datetime

def get_reset_datetime() -> datetime.datetime:
	'''
	Get the `datetime` object representing when the current swapping day started

	@returns The `datetime` object
	'''
	
	reset_date = datetime.datetime.now(datetime.timezone.utc).replace(hour = 4, minute = 0, second = 0, microsecond = 0)
	if (reset_date > datetime.datetime.now(datetime.timezone.utc)): reset_date = reset_date - datetime.timedelta(days = 1)

	return reset_date

def get_paddle_datetime() -> datetime.datetime:
	'''
	Get the `datetime` object representing when Shakepay started counting swaps for the paddles

	@returns The `datetime` object
	'''

	return datetime.datetime(2021, 5, 3, 4, tzinfo = datetime.timezone.utc)

def get_swap_datetime() -> datetime.datetime:
	'''
	Get the `datetime` object representing when Shakepay started the waitlist

	@returns The `datetime` object
	'''

	return datetime.datetime(2021, 4, 21, 4, tzinfo = datetime.timezone.utc)

def string_to_datetime(string: str) -> datetime.datetime:
	'''
	Converts an ISO 8601 string into a datetime object

	@returns The `datetime` object in UTC
	'''

	datetime_obj = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
	datetime_obj = datetime_obj.replace(tzinfo = datetime.timezone.utc)

	return datetime_obj

def epoch_to_datetime(epoch: float) -> datetime.datetime:
	'''
	Converts an epoch timestamp into a datetime object

	@returns The `datetime` object
	'''

	return datetime.datetime.utcfromtimestamp(epoch)