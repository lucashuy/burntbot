import time
import sys
import secrets
import getpass

import globals
import bot
import webui

from service.requests.users import users
from service.requests.wallet import get_wallet
from service.requests.login import pre_login, mfa_login
from service.persistence import read_persistence, upsert_persistence
from service.log import log
from service.decode_payload import decode

def read_flags():
	for arg in sys.argv[1:]:
		if (arg == '-v'):
			log(f'-v setting verbose logging')
			globals.flags['verbose'] = True
		elif (arg == '-l'):
			log(f'-l setting listen only mode - no auto returns')
			globals.flags['listen'] = True
		elif (arg[0:2] == '-r') and ('=' in arg) and (':' in arg):
			split_args = arg.split('=')
			split_args = split_args[1].split(':')
			
			log(f'-r setting web ui host to {split_args[0]} on port {split_args[1]}')

			globals.webui_host = split_args[0]
			globals.webui_port = split_args[1]

		else:
			log(f'Unknown argument: {arg}')
			raise SystemExit(0)

def load_persistence_data():
	persistence = {}

	# read or create persistence file
	try:
		log('Reading persistence file')
		persistence = read_persistence()
	except: pass

	# add required keys incase we need to login
	if (not 'unique_id' in persistence): persistence['unique_id'] = secrets.token_hex(8)
	if (not 'serial_number' in persistence): persistence['serial_number'] = secrets.token_hex(9)

	# set the device headers here since we need them just incase we login
	globals.headers['X-Device-Unique-Id'] = persistence['unique_id']
	globals.headers['X-Device-Serial-Number'] = persistence['serial_number']

	# check if we have an existing session
	if (not 'token' in persistence) or (persistence['token'] == ''):
		log('Existing session not found, logging in to Shakepay...')

		password = getpass.getpass('> password: ')
		email = input('> email: ')

		try:
			pre_auth_token = pre_login(email, password)

			code = input('> 2FA code: ')

			persistence['token'] = mfa_login(code, pre_auth_token)
		except:
			log('Failed to login, stopping')
			raise SystemExit(0)
	
	# set token header
	globals.headers['Authorization'] = persistence['token']

	# add other key values to persistence
	user_id = decode(persistence['token'].split('.')[1])['userId']

	log(f'userid is {user_id}', True)

	user_data = users(user_id)

	log(user_data, True)

	if (not 'shaketag' in persistence): persistence['shaketag'] = f'@{user_data["username"]}'
	if (not 'note' in persistence): persistence['note'] = ''
	if (not 'poll_rate' in persistence): persistence['poll_rate'] = 10
	if (not 'wallet_id' in persistence): persistence['wallet_id'] = get_wallet()['id']

	# set global variables
	globals.note = persistence['note']
	globals.poll_rate = persistence['poll_rate']
	globals.shaketag = persistence['shaketag']
	globals.wallet_id = persistence['wallet_id']

	# save data
	upsert_persistence(persistence)

def read_version() -> str:
	version = '0.0.0'

	try:
		log('Reading version')
		with open('.version') as file:
			version = file.readline()
	except: pass

	return version

if (__name__ == '__main__'):
	read_flags()
	load_persistence_data()
	globals.version = read_version()

	# start ui thread
	log('Starting WebUI')
	ui = webui.WebUI()
	ui.start()

	swap_bot = bot.SwapBot()
	swap_bot.start()

	# main thread busy
	while (1):
		time.sleep(10)

		if (not ui.is_alive()):
			log('Restarting WebUI')

			ui = webui.WebUI()
			ui.start()

		if (not swap_bot.is_alive()):
			log('Bot died, stopping program')

			raise SystemExit(0)