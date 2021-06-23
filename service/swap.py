import globals

from service.log import log
from service.requests.labrie_check import labrie_check
from service.requests.transactions import send_transaction

class Map(dict):
	def __missing__(self, key): return key

# returns None if okay, otherwise string reason failed against database check
def swap(shaketag: str, amount: float, override: bool = False, is_return: bool = True, custom_note = None):
	note = None

	if (not custom_note == None):
		note = custom_note
	else:
		note = globals.bot_note.format_map(Map(shaketag = shaketag, amount = '${}'.format(amount)))

	pass_check = True
	
	# check shaketag against DB if enabled
	if (globals.bot_return_check):
		# query DB
		response = labrie_check(shaketag, 'return')

		if (response['success']):
			pass_check = response['data']['allow_return' if is_return else 'allow_initiate']

	if (pass_check or override):
		if (globals.bot_flags['listen']):
			log(f'Simulate sending ${amount} to {shaketag} with note: {note}')
		else:
			log(f'Sending ${amount} to {shaketag}')
			send_transaction(amount, shaketag, note)
	else:
		reason = response['data']['reason'] or ''
		log(f'Ignoring swap for {shaketag} for reason: {reason}')

		return reason

	return None