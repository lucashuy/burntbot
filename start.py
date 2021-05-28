#!/usr/bin/python3

import time
import json

import globals
import logic_service
import logic_requests

import bot

_PERSISTENCE_FILE_NAME = '.persistence'

def save_persistence(data: dict):
	with open(_PERSISTENCE_FILE_NAME, 'w') as file:
		file.write(json.dumps(data))

if (__name__ == '__main__'):
	persistence = None

	# read or create persistence file
	try:
		with open(_PERSISTENCE_FILE_NAME) as file:
			logic_service.printt('Reading persistence file')

			persistence = json.loads(file.readline())
	except:
		logic_service.printt('Creating new persistence file')

		persistence = {
			'token': '',
			'poll_rate': globals.POLL_RATE,
			'note': globals.NOTE
		}

		save_persistence(persistence)

	# check if the file is valid (we have token key)
	if (not 'token' in persistence) or (persistence['token'] == ''):
		logic_service.printt('No token found, stopping')
		raise SystemExit(0)
	
	# set global variables
	globals.NOTE = persistence['note']
	globals.POLL_RATE = persistence['poll_rate']

	# set the authorization header
	globals.HEADERS['Authorization'] = persistence['token']

	# validate valid token by getting wallet ID
	logic_service.printt('Getting CAD wallet ID')
	globals.WALLET_ID = logic_requests.wallet()

	# start bot thread
	logic_service.printt('Starting bot')

	bot = bot.SwapBot()
	bot.start()

	# main thread busy
	while (1):
		if (not bot.is_alive()):
			logic_service.printt('Bot died, stopping')
			break

		time.sleep(1)