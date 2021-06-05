import datetime

def get_reset_datetime() -> datetime.datetime:
	reset_date = datetime.datetime.now(datetime.timezone.utc).replace(hour = 4, minute = 0, second = 0, microsecond = 0)
	if (reset_date > datetime.datetime.now(datetime.timezone.utc)): reset_date = reset_date - datetime.timedelta(days = 1)

	return reset_date

def string_to_datetime(string: str) -> datetime.datetime:
	datetime_obj = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
	datetime_obj = datetime_obj.replace(tzinfo = datetime.timezone.utc)

	return datetime_obj
