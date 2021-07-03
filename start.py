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

def read_flags():
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

	if (not 'shaketag' in persistence): persistence['shaketag'] = f'@{user_data["username"]}'
	if (not 'note' in persistence): persistence['note'] = ''
	if (not 'blacklist' in persistence): persistence['blacklist'] = {}
	if (not 'poll_rate' in persistence): persistence['poll_rate'] = 10
	if (not 'wallet_id' in persistence): persistence['wallet_id'] = get_wallet()['id']
	if (not 'bot_return_check' in persistence): persistence['bot_return_check'] = False
	if (not 'shaking_sats_enabled' in persistence): persistence['shaking_sats_enabled'] = False
	if (not 'heart_beat' in persistence): persistence['heart_beat'] = False
	if (not 'heart_beat_swaps' in persistence): persistence['heart_beat_swaps'] = False
	if (not 'heart_beat_points' in persistence): persistence['heart_beat_points'] = False
	if (not 'heart_beat_position' in persistence): persistence['heart_beat_position'] = False

	# set global variables
	globals.bot_note = persistence['note']
	globals.bot_poll_rate = persistence['poll_rate']
	globals.shaketag = persistence['shaketag']
	globals.wallet_id = persistence['wallet_id']
	globals.bot_blacklist = persistence['blacklist']
	globals.bot_return_check = persistence['bot_return_check']
	globals.shaking_sats_enabled = persistence['shaking_sats_enabled']
	globals.heart_beat_enabled = persistence['heart_beat']
	globals.heart_beat_swaps = persistence['heart_beat_swaps']
	globals.heart_beat_points = persistence['heart_beat_points']
	globals.heart_beat_position = persistence['heart_beat_position']

	# save data
	upsert_persistence(persistence)

if (__name__ == '__main__'):
	read_flags()
	load_persistence_data()

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