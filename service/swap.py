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
		note = globals.note.format_map(Map(shaketag = shaketag, amount = '${}'.format(amount)))

	response = labrie_check(shaketag, 'return')
	do_send = response['data']['allow_return' if is_return else 'allow_initiate']

	if (response['success'] and do_send) or (override):
		if (globals.flags['listen']):
			log(f'Simulate sending ${amount} to {shaketag} with note: {note}')
		else:
			log(f'Sending ${amount} to {shaketag}')
			send_transaction(amount, shaketag, note)
	else:
		reason = response['data']['reason'] or ''
		log(f'Ignoring swap for {shaketag} for reason: {reason}')

		return reason

	return None