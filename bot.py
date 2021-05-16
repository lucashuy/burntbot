#!/usr/bin/python3

import os
import datetime
import time

import requests_methods
import service

from dotenv import load_dotenv
load_dotenv()

_POLL_RATE = int(os.getenv('POLL_RATE', 10))
_INIT_FETCH_AMNT = os.getenv('INIT_FETCH_AMNT', 50)
_NOTE = os.getenv('NOTE', '')

# create constants for API endpoints
HOST = 'https://api.shakepay.com/'
ENDPOINTS = {
	'WALLET': HOST + 'wallets',
	'HISTORY': HOST + 'transactions/history',
	'SWAP': HOST + 'transactions'
}

# init required headers from .env file
HEADERS = {
	'User-Agent': os.getenv('USER_AGENT'),
	'X-Device-Unique-Id': os.getenv('UNIQUE_ID'),
	'X-Device-Serial-Number': os.getenv('SERIAL_NUM')
}

# JWT
TOKEN = None

# CAD wallet ID
WALLET_ID = None

# trading history hash table
HISTORY = {}

class map(dict):
	def __missing__(self, key): return key

def init_history():
	page_num = 1

	body = {
		'filterParams': {'type': 'peer'},
		'pagination': {
			'descending': True,
			'page': page_num,
			'rowsPerPage': _INIT_FETCH_AMNT
		}
	}

	# the datetime at which reset happened (4am UTC time)
	reset_date = datetime.datetime.now(datetime.timezone.utc).replace(hour = 4, minute = 0, second = 0, microsecond = 0)
	if (reset_date > datetime.datetime.now(datetime.timezone.utc)): reset_date = reset_date - datetime.timedelta(days = 1)

	while (1):
		# get transaction history 50 at a time
		response = requests_methods.history(ENDPOINTS['HISTORY'], HEADERS, TOKEN, body)

		# populate the HISTORY object
		service.filter_transactions(response, HISTORY, reset_date)

		# get last transaction timestamp in datetime format with UTC timezone
		last_transaction_datetime = service.to_datetime(response['data'][-1]['timestamp'])

		service.printt('Fetched page {} (lasttime: {})'.format(page_num, str(last_transaction_datetime)))

		# stop loop if we dont have anymore valid transactions
		if (response == {} or last_transaction_datetime < reset_date):
			break

		page_num = page_num + 1
		body['pagination']['page'] = page_num

if (__name__ == '__main__'):
	# read token from file
	try:
		with open('./.token') as token_file:
			service.printt('Reading .token')
			TOKEN = token_file.readline()
	except FileNotFoundError:
		service.printt('.token file not found')
		raise SystemExit(0)
	
	# fetch CAD wallet ID (for transactions)
	service.printt('Getting CAD wallet ID')
	WALLET_ID = requests_methods.wallet(ENDPOINTS['WALLET'], HEADERS, TOKEN)

	# init hash table of transactions
	service.printt('Initializing swap history today')
	init_history()
	
	# wait for rate limit cooldown (for transactions its 15/minute)
	service.printt('Waiting 60 seconds for rate limit expiry')
	time.sleep(60)
	service.printt('Bot ready')

	while (1):
		response_json = requests_methods.history(ENDPOINTS['HISTORY'], HEADERS, TOKEN, {'filterParams': {'currencies': ['CAD']}})
		swap_list = service.filter_transactions(response_json, HISTORY)

		for shaketag in swap_list:
				amount = swap_list[shaketag]
				note = _NOTE.format_map(map(shaketag = shaketag, amount = amount))

				requests_methods.send_transaction(ENDPOINTS['SWAP'], HEADERS, TOKEN, amount, WALLET_ID, shaketag, note)
				#service.printt('Simulate sending ${} to {} with note:  ({}) (currswap: {})'.format(amount, shaketag, note, HISTORY[shaketag]['swap']))

		time.sleep(_POLL_RATE)