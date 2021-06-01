#!/usr/bin/python3

import time

import globals
import logic_service
import logic_requests

import bot

if (__name__ == '__main__'):
	persistence = None

	# read or create persistence file
	try:
		logic_service.printt('Reading persistence file')
		logic_service.read_persistence()
	except:
		logic_service.printt('Creating new persistence file')

		# save defaults
		persistence = {
			'token': '',
			'poll_rate': globals.POLL_RATE,
			'note': globals.NOTE
		}

		logic_service.upsert_persistence(persistence)

	# check if the file is valid (we have token key)
	if (not 'token' in persistence) or (persistence['token'] == ''):
		logic_service.printt('No token found, stopping')
		raise SystemExit(0)
	
	# set global variables
	globals.NOTE = persistence['note'] or globals.NOTE
	globals.POLL_RATE = persistence['poll_rate'] or globals.POLL_RATE

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

		time.sleep(10)