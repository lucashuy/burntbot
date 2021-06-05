import requests
import json

import globals

from service.requests.exception import raise_exception
from service.log import log

def login(email: str, password: str, code: str) -> str:
	# copy headers to append content type
	local_headers = globals.HEADERS.copy()
	local_headers['Content-Type'] = 'application/json'

	# pre 2FA POST
	response = requests.post(globals.ENDPOINT_AUTHENTICATE, headers = local_headers, data = json.dumps({
		'password': password,
		'strategy': 'local',
		'totpType': 'sms',
		'username': email
	}))

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when login (pre 2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()

	local_headers['Authorization'] = response['accessToken']

	# 2FA POST
	response = requests.post(globals.ENDPOINT_AUTHENTICATE, headers = local_headers, data = json.dumps({
		'mfaToken': code,
		'strategy': 'mfa'
	}))

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when login (2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()

	return response['accessToken']