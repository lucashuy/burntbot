#!/usr/bin/python3

import os
import datetime
import time

import requests_methods
import filter_transactions

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
	#TODO rewrite this reset_date mess below
	reset_date = datetime.datetime.now(datetime.timezone.utc).replace(hour = 4, minute = 0, second = 0, microsecond = 0)
	if (reset_date > datetime.datetime.now(datetime.timezone.utc)): reset_date = reset_date - datetime.timedelta(days = 1)

	while (1):
		# get transaction history 50 at a time
		response = requests_methods.history(ENDPOINTS['HISTORY'], HEADERS, TOKEN, body)

		# populate the HISTORY object
		filter_transactions.filter_transactions(response, HISTORY, reset_date)

		# get last transaction timestamp in datetime format with UTC timezone
		last_transaction_datetime = datetime.datetime.strptime(response['data'][-1]['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
		last_transaction_datetime = last_transaction_datetime.replace(tzinfo = datetime.timezone.utc)

		print('++ Fetched page {} (reftime: {}, lasttime: {})'.format(page_num, str(reset_date), str(last_transaction_datetime)))

		# stop loop if we dont have anymore valid transactions
		if (response == {} or last_transaction_datetime < reset_date):
			break

		page_num = page_num + 1
		body['pagination']['page'] = page_num

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
	print('+ Bot ready')

	# init hash table of transactions
	print('+ Initializing swap history today')
	init_history()
	
	print(HISTORY)

	print('+ Waiting 60 seconds for rate limit expiry')
	# time.sleep(60)
	print('+ Starting polling')

	while (1):
		response_json = requests_methods.history(ENDPOINTS['HISTORY'], HEADERS, TOKEN, {'filterParams': {'currencies': ['CAD']}})
		swap_list = filter_transactions.filter_transactions(response_json, HISTORY)

		for transaction in swap_list:
			transaction_id = transaction['transactionId']
			shaketag = transaction['from']['label']
			user_id = transaction['from']['id']

			print('++ Simulate sending ${} to {} ({}) (currswap: {})'.format(transaction['amount'], shaketag, user_id, HISTORY[shaketag]['swap']))

		print('wait')
		time.sleep(10)