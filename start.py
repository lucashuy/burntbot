import time
import sys
import secrets
import getpass

import globals

from classes.bot import SwapBot
from classes.webui import WebUI
from classes.shaker import ShakingSats
from classes.heartbeat import HeartBeat
from classes.version import Version

from api.exception import ClientException
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

def _login():
	email = input('> Email: ')
	password = getpass.getpass('> Password: ')

	try:
		pre_auth_token = pre_login(email, password)

		while (pre_auth_token == False):
			log('Please check your email for an email from Shakepay to authenticate the IP address!')
			input('> Press ENTER when you confirmed the IP address...')
			
			pre_auth_token = pre_login(email, password)
			log('Checking...')

		code = input('> 2FA code: ')

		return mfa_login(code, pre_auth_token)
	except Exception as e:
		log(f'Failed to login, stopping: {e}')
		raise SystemExit(0)

def _load_persistence_data():
	persistence = {}

	def bind_setting(key: str, value, globals_name = None):
		if (not key in persistence): persistence[key] = value
		setattr(globals, globals_name or key, persistence[key])

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
		persistence['token'] = _login()
	
	# set token header
	globals.headers['Authorization'] = persistence['token']

	# add other key values to persistence
	globals.user_id = decode(persistence['token'].split('.')[1])['userId']

	log(f'userid is {globals.user_id}', True)

	user_data = None

	while (user_data == None):
		try:
			log('Getting user data...')
			user_data = users(globals.user_id)
		except ClientException:
			log('Invalid session, logging into Shakepay again...')
			persistence['token'] = _login()
		except Exception as e:
			log(f'Failed to get user data, stopping: {e}')
			raise SystemExit(0)

	log(user_data, True)
	
	bind_setting('shaketag', f'@{user_data["username"]}')
	bind_setting('note', '', 'bot_note')
	bind_setting('blacklist', {}, 'bot_blacklist')
	bind_setting('poll_rate', 10, 'bot_poll_rate')
	bind_setting('wallet_id', get_wallet()['id'])
	bind_setting('bot_return_check', False)
	bind_setting('shaking_sats_enabled', False)
	bind_setting('heart_beat', False, 'heart_beat_enabled')
	bind_setting('heart_beat_swaps', False)
	bind_setting('heart_beat_points', False)
	bind_setting('heart_beat_position', False)
	bind_setting('bot_send_list', {})
	bind_setting('list_note', '')
	
	# save data
	upsert_persistence(persistence)

def _print_startup():
	log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	log('\tburntbot, created by @burnttoaster')
	log(f'\tv{globals.version}')
	log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

if (__name__ == '__main__'):
	# read version in
	try:
		with open('./.version') as file:
			globals.version = Version(file.read().strip())
	except: pass

	# update user agent header
	globals.headers['User-Agent'] = f'Shakepay App v1.6.100 (16100) on burntbot ({globals.version})'
	
	_print_startup()
	_read_flags()
	_load_persistence_data()

	# start bot thread
	swap_bot = SwapBot()
	swap_bot.start()

	# initialize ui thread
	ui = WebUI()

	# initialize shake thread
	shaking_sats = ShakingSats()

	# initialize heart beat thread
	api_heart_beat = HeartBeat()

	# main thread busy
	while (1):
		time.sleep(10)

		if (globals.bot_state):
			if (not ui.is_alive()):
				log('Started web UI thread')

				ui = WebUI()
				ui.start()

			if (not shaking_sats.is_alive()) and (globals.shaking_sats_enabled):
				log('Started shaking sats thread')

				shaking_sats = ShakingSats()
				shaking_sats.start()

			if (not api_heart_beat.is_alive()) and (globals.heart_beat_enabled) and (not globals.bot_flags['listen']):
				log('Started heart beat thread')

				api_heart_beat = HeartBeat()
				api_heart_beat.start()
		else:
			if (shaking_sats.is_alive()):
				log('Stopping shaking sats thread')

				shaking_sats.stop.set()

			if (api_heart_beat.is_alive()):
				log('Stopping heart beat thread')

				api_heart_beat.stop.set()

		if (not swap_bot.is_alive()):
			log('Bot died, stopping program')

			raise SystemExit(0)
