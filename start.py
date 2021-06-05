#!/usr/bin/python3

import time

import globals
import bot

from service.requests.wallet import get_wallet
from service.persistence import read_persistence, upsert_persistence
from service.log import log

if (__name__ == '__main__'):
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
			'poll_rate': globals.POLL_RATE,
			'note': globals.NOTE
		}

		upsert_persistence(persistence)

	# check if the file is valid (we have token key)
	if (not 'token' in persistence) or (persistence['token'] == ''):
		log('No token found, stopping')
		raise SystemExit(0)
	
	# set global variables
	globals.NOTE = persistence['note'] or globals.NOTE
	globals.POLL_RATE = persistence['poll_rate'] or globals.POLL_RATE

	# set the authorization header
	globals.HEADERS['Authorization'] = persistence['token']

	# validate valid token by getting wallet ID
	log('Getting CAD wallet ID')
	globals.WALLET_ID = get_wallet()['id']

	# start bot thread
	log('Starting bot')

	bot = bot.SwapBot()
	bot.start()

	# main thread busy
	while (1):
		if (not bot.is_alive()):
			log('Bot died, stopping')
			break

		time.sleep(10)