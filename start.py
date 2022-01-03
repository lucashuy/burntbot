import time
import sys
import secrets
import getpass
import sqlite3

import globals

from classes.bot import SwapBot
from classes.webui import WebUI
from classes.shaker import ShakingSats
from classes.heartbeat import HeartBeat
from classes.sqlite import SQLite
from classes.version import Version

from api.exception import ClientException
from api.users import users
from api.wallet import get_wallet
from api.login import pre_login, mfa_login
from api.version import get_master_version
from utilities.persistence import read_version
from utilities.log import log
from utilities.decode_payload import decode
from utilities.migrations import migrate

def _read_flags():
	'''
	Function to read in and parse startup options
	'''
	
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
		elif (arg == '-d') or (arg == '--demo'):
			log(f'-d enabling demo mode - no Shakepay functionality')
			globals.bot_flags['demo'] = True
		else:
			log(f'Unknown argument: {arg}')
			raise SystemExit(0)

def _login_helper():
	'''
	Helper function to login to Shakepay
	'''

	# user input
	email = input('> Email: ')
	password = getpass.getpass('> Password: ')

	try:
		# get the initial token to login
		pre_auth_token = pre_login(email, password)

		# if function returns false, then we need to verify IP address
		while (pre_auth_token == False):
			log('Please check your email for an email from Shakepay to authenticate the IP address!')
			input('> Press ENTER when you confirmed the IP address...')
			
			# attempt to get a new token after user confirmation
			log('Checking...')
			pre_auth_token = pre_login(email, password)

		# email confirmed/not needed, ask for 2FA code
		code = input('> 2FA code: ')

		# return final token after login with code
		return mfa_login(code, pre_auth_token)
	except Exception as e:
		log(f'Failed to login, stopping: {e}')
		raise SystemExit(0)

def _login():
	'''
	Main logic to login to Shakepay and save token data
	'''

	db = SQLite()

	# get existing device headers if they exist, otherwise create them
	globals.headers['X-Device-Unique-Id'] = db.get_key_value('unique_id') or secrets.token_hex(8)
	globals.headers['X-Device-Serial-Number'] = db.get_key_value('serial_number') or secrets.token_hex(9)

	# get token if exists
	globals.headers['Authorization'] = db.get_key_value('token')
	
	# test the token by getting user info
	user_data = None
	while (user_data == None):
		try:
			# get user id from token (used to get user data)
			user_id = decode(globals.headers['Authorization'].split('.')[1])['userId']

			# get user data
			user_data = users(user_id)
		except (ClientException, AttributeError):
			# 4xx HTTP error, get a new token and device ids
			globals.headers['X-Device-Unique-Id'] = secrets.token_hex(8)
			globals.headers['X-Device-Serial-Number'] = secrets.token_hex(9)
			globals.headers['Authorization'] = _login_helper()
		except Exception as e:
			log(f'Failed to get user data, stopping: {e}')
			raise SystemExit(0)

	# load shaketag and wallet id into RAM
	globals.shaketag = f'@{user_data["username"]}'
	globals.wallet_id = get_wallet()['id']

	# write auth data into db
	db.upsert_key_value('token', globals.headers['Authorization'])
	db.upsert_key_value('unique_id', globals.headers['X-Device-Unique-Id'])
	db.upsert_key_value('serial_number', globals.headers['X-Device-Serial-Number'])

	db.commit()
	db.close()

def _print_startup():
	log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	log('\tburntbot, created by @burnttoaster')
	log(f'\tv{globals.version}')
	log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	
def _version_check():
	'''
	Checks if the bot is being run correctly and is not out of date
	'''

	master_version = Version(str(get_master_version()))
	if (globals.version < master_version):
		log(f'\nHey, theres a new version ({master_version}) of the bot availible to download!\n')

	python_version = Version(sys.version.split(' ')[0])
	if (python_version < Version('3.6.0')):
		log(f'\nYou are running a version of Python that is too old ({python_version})! Please make sure you are running at least 3.6.15!\n')
		raise SystemExit()

	sqlite_version = Version(sqlite3.sqlite_version)
	if (sqlite_version < Version('3.24.0')):
		log(f'\nYou have a version of SQLite3 that is too old ({sqlite_version})! Try installing a newer version of Python or replace the SQLite3 executable with one that is at least 3.24.0!\n')
		raise SystemExit()

if (__name__ == '__main__'):
	globals.version = read_version()
	globals.headers['User-Agent'] = f'Shakepay App v1.6.100 (16100) on burntbot ({globals.version})'

	_print_startup()
	_version_check()

	_read_flags()

	# artificial delay
	time.sleep(3)

	# only run migrations and login if we are not in demo mode
	if (globals.bot_flags['demo'] == False):
		migrate()
		_login()

	# initialize threads
	swap_bot = SwapBot()
	ui = WebUI()
	shaking_sats = ShakingSats()
	api_heart_beat = HeartBeat()

	# initialize database
	db = SQLite()

	# main thread busy
	try:
		# start bot if the bot is not in demo mode
		if (globals.bot_flags['demo'] == False):
			swap_bot.start()

			while (1):
				# bot has own restart code, if it fails that means something is wrong
				if (not swap_bot.is_alive()):
					log('Bot died, stopping program')

					raise SystemExit(0)

				if (SwapBot.bot_state):
					if (not ui.is_alive()):
						log('Started web UI thread')

						ui = WebUI()
						ui.start()

					if (not shaking_sats.is_alive()) and (db.get_key_value('shaking_sats')):
						log('Started shaking sats thread')

						shaking_sats = ShakingSats()
						shaking_sats.start()

					if (not api_heart_beat.is_alive()) and (db.get_key_value('heart_beat')) and (not globals.bot_flags['listen']):
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

				time.sleep(10)
		else:
			# bot is in demo mode, only run the web ui
			while (1):
				if (not ui.is_alive()):
					log('Started web UI thread')

					ui = WebUI()
					ui.start()

				time.sleep(10)
	except KeyboardInterrupt:
		print()
	finally:
		log('Stopping gracefully')

		if (swap_bot.is_alive()): swap_bot.stop.set()
		if (shaking_sats.is_alive()): shaking_sats.stop.set()
		if (api_heart_beat.is_alive()): api_heart_beat.stop.set()

		# wait for processes to finish up
		#time.sleep(1) # this probably doesnt work

		db.commit()
		db.close()
		log('Saved data')
