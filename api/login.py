import requests
import json

import globals

from api.exception import raise_exception
from utilities.log import log

# returns False on email verification
# returns accessToken for 2FA on success
def pre_login(email: str, password: str):
	# copy headers to append content type
	local_headers = globals.headers.copy()
	local_headers['Content-Type'] = 'application/json'
	local_headers['X-Device-Model'] = 'SM-G930W8'
	local_headers['X-Device-System-Name'] = 'Android'
	local_headers['X-Device-System-Version'] = '8.0.0'

	# pre 2FA POST
	response = requests.post('https://api.shakepay.com/authentication', headers = local_headers, data = json.dumps({
		'password': password,
		'strategy': 'local',
		'totpType': 'sms',
		'username': email
	}))

	if (response.status_code == 403):
		return False
	elif (not response.ok):
		log('Something went wrong when login (pre 2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()
	return response['accessToken']

def mfa_login(code: str, pre_token: str) -> str:
	# copy headers to append content type
	local_headers = globals.headers.copy()
	local_headers['Content-Type'] = 'application/json'
	local_headers['Authorization'] = pre_token
	local_headers['X-Device-Model'] = 'SM-G930W8'
	local_headers['X-Device-System-Name'] = 'Android'
	local_headers['X-Device-System-Version'] = '8.0.0'

	# 2FA POST
	response = requests.post('https://api.shakepay.com/authentication', headers = local_headers, data = json.dumps({
		'mfaToken': code,
		'strategy': 'mfa'
	}))

	# make sure we have 2xx status
	if (not response.ok):
		log('Something went wrong when login (2FA): {}'.format(response.text))
		
		raise_exception(response.status_code)

	response = response.json()

	return response['accessToken']
