import time
import sys
import secrets
import getpass

import globals

from classes.bot import SwapBot
from classes.webui import WebUI
from classes.shaker import ShakingSats
from classes.heartbeat import HeartBeat

from api.users import users
from api.wallet import get_wallet
from api.login import pre_login, mfa_login
from utilities.persistence import read_persistence, upsert_persistence
from utilities.log import log
from utilities.decode_payload import decode

def _read_flags():
	for arg in sys.argv[1:]:
		if (arg == '-v') or (arg == '--verbose'):
			log(f'-v setting verbose logging')
			globals.bot_flags['verbose'] = True
		elif (arg == '-l') or (arg == '--listen'):
			log(f'-l setting listen only mode - no auto returns')
			globals.bot_flags['listen'] = True
		elif (arg[0:2] == '-r') and ('=' in arg) and (':' in arg):
			split_args = arg.split('=')
			split_args = split_args[1].split(':')
			
			log(f'-r setting web ui host to {split_args[0]} on port {split_args[1]}')

			globals.webui_host = split_args[0]
			globals.webui_port = split_args[1]
		else:
			log(f'Unknown argument: {arg}')
			raise SystemExit(0)

def _load_persistence_data():
	persistence = {}

	def bind_setting(key: str, value):
		if (not key in persistence): persistence[key] = value
		setattr(globals, key, persistence[key])

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

		password = getpass.getpass('> Password: ')
		email = input('> Email: ')

		try:
			pre_auth_token = pre_login(email, password)

			if (pre_auth_token == False):
				log('Please check your email for an email from Shakepay to authenticate the IP address!')
				input('> Press ENTER when you confirmed the IP address...')
				
				pre_auth_token = pre_login(email, password)

			code = input('> 2FA code: ')

			persistence['token'] = mfa_login(code, pre_auth_token)
		except Exception as e:
			log(f'Failed to login, stopping: {e}')
			raise SystemExit(0)
	
	# set token header
	globals.headers['Authorization'] = persistence['token']

	# add other key values to persistence
	globals.user_id = decode(persistence['token'].split('.')[1])['userId']

	log(f'userid is {globals.user_id}', True)

	user_data = users(globals.user_id)

	log(user_data, True)
	
	bind_setting('shaketag', f'@{user_data["username"]}')
	bind_setting('note', '')
	bind_setting('blacklist', {})
	bind_setting('poll_rate', 10)
	bind_setting('wallet_id', get_wallet()['id'])
	bind_setting('bot_return_check', False)
	bind_setting('shaking_sats_enabled', False)
	bind_setting('heart_beat', False)
	bind_setting('heart_beat_swaps', False)
	bind_setting('heart_beat_points', False)
	bind_setting('heart_beat_position', False)
	
	# save data
	upsert_persistence(persistence)

if (__name__ == '__main__'):
	_read_flags()
	_load_persistence_data()

	# read version in
	try:
		with open('./.version') as file:
			globals.version = file.read()
	except: pass

	# start ui thread
	log('Starting WebUI')
	ui = WebUI()
	ui.start()

	# start bot thread
	swap_bot = SwapBot()
	swap_bot.start()

	# initialize shake thread
	shaking_sats = ShakingSats()

	# initialize heart beat thread
	api_heart_beat = HeartBeat()

	# main thread busy
	while (1):
		time.sleep(10)

		if (not ui.is_alive()):
			log('WebUI is down, restarting thread')

			ui = WebUI()
			ui.start()

		if (not swap_bot.is_alive()):
			log('Bot died, stopping program')

			raise SystemExit(0)

		if (not shaking_sats.is_alive()) and (globals.shaking_sats_enabled) and (globals.bot_state):
			log('Starting shaking sats thread')

			shaking_sats = ShakingSats()
			shaking_sats.start()

		if (not api_heart_beat.is_alive()) and (globals.heart_beat_enabled) and (globals.bot_state) and (not globals.bot_flags['listen']):
			log('Starting heart beat thread')

			api_heart_beat = HeartBeat()
			api_heart_beat.start()