#!/usr/bin/python3

import os
import time

import requests_methods
import generate_credit_list

from dotenv import load_dotenv
load_dotenv()


# create constants for API endpoints
HOST = 'https://api.shakepay.com/'
ENDPOINTS = {
	'AUTH': HOST + 'authentication',
	'WALLET': HOST + 'wallets',
	'HISTORY': HOST + 'transactions/history'
}

# init required headers from .env file
HEADERS = {
	'User-Agent': os.getenv('USER_AGENT'),
	'X-Device-Unique-Id': os.getenv('UNIQUE_ID'),
	'X-Device-Serial-Number': os.getenv('SERIAL_NUM')
}

# JWT
TOKEN = None

if (__name__ == '__main__'):
	# read token from file
	try:
		with open('./.token') as token_file:
			print('+ Reading .token')
			TOKEN = token_file.readline()
	except FileNotFoundError:
		print('! .token file not found')
		raise SystemExit(0)
	
	# bot ready
	print('+ Bot ready ({})'.format(TOKEN))

	# main loop starts here
	while (1):
		time.sleep(10)