import requests
import json
import socket

import globals

from utilities.log import log

def shaking_sats():
	# copy global headers so that we can append our own headers without affecting global
	local_headers = {**globals.headers, **{
		'X-Device-Brand': 'bot',
		'X-Device-Model': socket.gethostname(),
		'X-Device-System-Name': 'burntbot',
		'X-Device-System-Version': str(globals.version),
		'X-Device-Carrier': '',
		'X-Device-Mac-Address': 'AA:BB:CC:DD:EE:FF',
		'X-Device-Manufacturer': '@burnttoaster',
		'X-Device-Id': '',
		'X-Device-Ip-Address': '10.0.0.1',
		'X-Device-Locale': 'en-CA',
		'X-Device-Country': 'CA',
		'X-Device-Name': f'@burnttoaster bot v{globals.version}',
		'X-Device-Total-Disk-Capacity': '138764288',
		'X-Device-Total-Memory': '37019976576',
		'X-Device-Is-Tablet': 'false',
		'X-Device-Has-Notch': 'false',
		'X-Notification-Token': '',
		'Content-Type': 'application/json'
	}}

	response = requests.post('https://api.shakepay.com/shaking-sats', headers = local_headers, data = json.dumps({}), timeout = 5)

	log(f'shaking-sats code: {response.status_code}', True)
	log(f'shaking-sats data: {response.json()}', True)