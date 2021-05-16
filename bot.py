#!/usr/bin/python3

import os
import datetime
import time

import requests_methods
import service

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

# trading history
# swap -1 == waiting on them
#       1 == need to send to them
#       0 == nothing outstanding
HISTORY = {}

def init_history():
	page_num = 1

	body = {
		'filterParams': {'type': 'peer'},
		'pagination': {
			'descending': True,
			'page': page_num,
			'rowsPerPage': 50
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

		service.printt('Fetched page {} (reftime: {}, lasttime: {})'.format(page_num, str(reset_date), str(last_transaction_datetime)))

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
	
	# bot ready
	service.printt('Bot ready')

	# init hash table of transactions
	service.printt('Initializing swap history today')
	init_history()
	
	for user in HISTORY:
		print('{} {}'.format(user, HISTORY[user]['swap']))

	service.printt('Waiting 60 seconds for rate limit expiry')
	# time.sleep(60)
	service.printt('Starting polling')

	while (1):
		response_json = requests_methods.history(ENDPOINTS['HISTORY'], HEADERS, TOKEN, {'filterParams': {'currencies': ['CAD']}})
		swap_list = service.filter_transactions(response_json, HISTORY)

		for shaketag in swap_list:
				user_id = HISTORY[shaketag]['user_id']
				amount = swap_list[shaketag]
				note = ''

				service.printt('Simulate sending ${} to {} ({}) (currswap: {})'.format(amount, shaketag, user_id, HISTORY[user]['swap']))

		time.sleep(10)