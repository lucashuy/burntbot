#!/usr/bin/python3

import requests
import os
import json

from dotenv import load_dotenv
load_dotenv()

# create constants for API endpoints
HOST = 'https://api.shakepay.com/'
ENDPOINTS = {
	'AUTH': HOST + 'authenticate',
	'WALLET': HOST + 'wallets'
}

# init required headers from .env file
HEADERS = {
	'User-Agent': 'Shakepay App v1.6.100 (16100) on samsung SM-G930W8 (Android 8.0.0)',
	'X-Device-Unique-Id': os.getenv('UNIQUE_ID'),
	'X-Device-Serial-Number': os.getenv('SERIAL_NUM')
}

# JWT
TOKEN = None

"""
Logins in to Shakepay using a 2FA code (from CLI) and returns the JWT
"""
def login(username, password):
	# copy headers so that we can add content type
	local_headers = HEADERS.copy()
	local_headers['Content-Type'] = 'application/json'

	# create JSON body for login (pre 2FA)
	body = json.dumps({
		'password': password,
		'username': username,
		'totpType': 'sms',
		'strategy': 'local'
	})

	print('+ Logging onto Shakepay')

	response_non_2fa = requests.post(ENDPOINTS['AUTH'], headers = HEADERS, data = body)

	# make sure we have 2xx status
	if (not response_non_2fa.ok):
		print('! Something went wrong when authenticating (pre 2FA)')
		raise SystemExit(0)

	# get 2FA token
	pre_2fa_token = response_non_2fa.json()['accessToken']
	
	code = None

	# query user input for 
	while (1):
		try:
			print('+ Please enter 2FA code')
			code = int(input('> '))

			# good code
			break
		except ValueError:
			print('! Invalid input')
		except EOFError:
			print('+ Stopping...')
			raise SystemExit(0)

	# add temp JWT to headers
	local_headers['Authorization'] = pre_2fa_token

	# create body for 2FA login
	body = json.dumps({
		'strategy': 'mfa',
		'mfaToken': code
	})

	print('+ Sending 2FA code')

	# get final JWT token
	response_2fa = requests.post(ENDPOINTS['AUTH'], headers = HEADERS, data = body)
	return response_2fa.json()['accessToken']


if (__name__ == '__main__'):
	try:
		with open('./.token') as token_file:
			TOKEN = token_file.readline()
	except FileNotFoundError:
		pass
	
	if (TOKEN == None):
		print('+ Missing JWT')

		TOKEN = login(os.getenv('USERNAME'), os.getenv('PASSWORD'))

		print('+ Got new token, saving in .token')

		with open('./.token', 'w') as token_file:
			token_file.write(TOKEN)

	print('+ Bot ready')