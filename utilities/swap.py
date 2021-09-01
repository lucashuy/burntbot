import globals

from utilities.log import log
from api.labrie_check import labrie_check
from api.transactions import send_transaction

class Map(dict):
	def __missing__(self, key): return key

def swap(shaketag: str, amount: float, note: str, do_labrie_check: bool, override: bool = False, is_return: bool = True):
	'''
	Swap with a user

	@param `shaketag` The shaketag of the user with the leading @
	@param `amount` The float amount to swap
	@param `note` The note to send along with the swap
	@param `do_labrie_check` Boolean indicating whether to check if they are a scammer/ghoster
	@param `override` (Optional) Override any warnings from scammer DB
	@param `is_return` (Optional) Is this swap a return or initiate

	@returns `None` if swap was okay, otherwise returns string containing reason why it did not
	'''
	mapped_note = note.format_map(Map(shaketag = shaketag, amount = '${}'.format(amount)))

	pass_check = True
	
	# check shaketag against DB if enabled
	if (do_labrie_check):
		# query DB
		response = labrie_check(shaketag, 'return')

		if (response['success']):
			# save response, either returns or initiate
			pass_check = response['data']['allow_return' if is_return else 'allow_initiate']

	if (pass_check or override):
		# swap if we pass the check or we overridden it

		if (globals.bot_flags['listen']):
			# dont swap if we are in listen mode, only print message
			log(f'Simulate sending ${amount} to {shaketag} with note: {mapped_note}')
		else:
			log(f'Sending ${amount} to {shaketag}')
			send_transaction(amount, shaketag, mapped_note)
	else:
		reason = response['data']['reason'] or ''
		log(f'Ignoring swap for {shaketag} for reason: {reason}')

		return reason

	return None