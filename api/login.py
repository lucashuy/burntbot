import requests
import json
import socket

import globals

from api.exception import raise_exception
from utilities.log import log

login_headers = {
	'X-Device-Brand': 'bot',
	'X-Device-Model': socket.gethostname(),
	'X-Device-System-Name': 'burntbot',
	'X-Device-Carrier': '',
	'X-Device-Mac-Address': 'AA:BB:CC:DD:EE:FF',
	'X-Device-Manufacturer': '@burnttoaster',
	'X-Device-Id': '',
	'X-Device-Ip-Address': '10.0.0.1',
	'X-Device-Locale': 'en-CA',
	'X-Device-Country': 'CA',
	'X-Device-Total-Disk-Capacity': '138764288',
	'X-Device-Total-Memory': '37019976576',
	'X-Device-Is-Tablet': 'false',
	'X-Device-Has-Notch': 'false',
	'X-Notification-Token': '',
	'Content-Type': 'application/json'
}

# returns False on email verification
# returns accessToken for 2FA on success
def pre_login(email: str, password: str):
	# set version since this function gets called after version is populated
	login_headers['X-Device-System-Version'] = str(globals.version)
	login_headers['X-Device-Name'] = f'@burnttoaster bot v{globals.version}'

	# copy global headers so that we can append our own headers without affecting global
	local_headers = {**globals.headers, **login_headers}

	# pre 2FA POST
	response = requests.post('https://api.shakepay.com/authentication', headers = local_headers, data = json.dumps({
		'password': password,
		'strategy': 'local',
		'totpType': 'sms',
		'username': email
	}), timeout = 5)

	if (response.status_code == 403):
		return False
	elif (not response.ok):
		log('Something went wrong when login (pre 2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()
	return response['accessToken']

def mfa_login(code: str, pre_token: str) -> str:
	# copy global headers so that we can append our own headers without affecting global
	local_headers = {**globals.headers, **login_headers}
	local_headers['Authorization'] = pre_token

	# 2FA POST
	response = requests.post('https://api.shakepay.com/authentication', headers = local_headers, data = json.dumps({
		'mfaToken': code,
		'strategy': 'mfa'
	}), timeout = 5)

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when login (2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()

	return response['accessToken']
