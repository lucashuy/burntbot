#!/usr/bin/python3

import time
import sys

import globals
import bot

from service.requests.wallet import get_wallet
from service.persistence import read_persistence, upsert_persistence
from service.log import log

def read_flags():
	for arg in sys.argv[1:]:
		if (arg == '-v'):
			log(f'-v setting verbose logging')
			globals.flags['verbose'] = True
		elif (arg == '-l'):
			log(f'-l setting listen only mode - no auto returns')
			globals.flags['listen'] = True
		else:
			log(f'Unknown argument: {arg}')
			raise SystemExit(0)

def read_per():
	persistence = {}

	# read or create persistence file
	try:
		log('Reading persistence file')
		persistence = read_persistence()
	except:
		log('Creating new persistence file')

		# save defaults
		persistence = {
			'token': '',
			'poll_rate': globals.poll_rate,
			'note': globals.note
		}

		upsert_persistence(persistence)

	return persistence

def read_version():
	version = '0.0.0'

	try:
		log('Reading version')
		with open('.version') as file:
			version = file.readline()
	except: pass

	return version

if (__name__ == '__main__'):
	read_flags()
	persistence = read_per()
	globals.version = read_version()

	# check if the file is valid (we have token key)
	if (not 'token' in persistence) or (persistence['token'] == ''):
		log('No token found, stopping')
		raise SystemExit(0)
	
	# set global variables
	globals.note = persistence['note'] or globals.note
	globals.poll_rate = persistence['poll_rate'] or globals.poll_rate

	# set the authorization header
	globals.headers['Authorization'] = persistence['token']

	# validate valid token by getting wallet ID
	log('Getting CAD wallet ID')
	globals.wallet_id = get_wallet()['id']

	# start bot thread
	log('Starting bot')

	swap_bot = bot.SwapBot()
	swap_bot.start()

	# main thread busy
	while (1):
		time.sleep(10)

		if (not swap_bot.is_alive()):
			if (swap_bot.restarts == -1):
				log('Bot died due to client error, stopping')

				raise SystemExit(0)
			elif (swap_bot.restarts < 5):
				swap_bot = bot.SwapBot()
				swap_bot.start()
			else:
				log('Bot died due to too many deaths, stopping')

				raise SystemExit(0)