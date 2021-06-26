import requests
import json

import globals

from utilities.log import log

def shaking_stats():
	# copy headers to append content type
	local_headers = globals.headers.copy()
	local_headers['X-Device-Brand'] = 'samsung'
	local_headers['X-Device-Model'] = 'SM-G930W8'
	local_headers['X-Device-System-Name'] = 'Android'
	local_headers['X-Device-System-Version'] = '8.0.0'
	local_headers['X-Device-Carrier'] = 'Bell'
	local_headers['X-Device-Mac-Address'] = 'AA:BB:CC:DD:EE:FF'
	local_headers['X-Device-Manufacturer'] = 'samsung'
	local_headers['X-Device-Id'] = 'universal8890'
	local_headers['X-Device-Ip-Address'] = '10.0.0.0'
	local_headers['X-Device-Locale'] = 'en-CA'
	local_headers['X-Device-Country'] = 'CA'
	local_headers['X-Device-Name'] = f'@burnttoaster bot v{globals.version}'
	local_headers['X-Device-Total-Disk-Capacity'] = '138764288'
	local_headers['X-Device-Total-Memory'] = '37019976576'
	local_headers['X-Device-Is-Tablet'] = 'false'
	local_headers['X-Device-Has-Notch'] = 'false'
	local_headers['X-Notification-Token'] = ''
	local_headers['Content-Type'] = 'application/json'

	response = requests.post(globals.endpoint_shaking_sats, headers = local_headers, data = json.dumps({}))

	log(f'shaking-sats code: {response.status_code}', True)
	log(f'shaking-sats data: {response.json()}', True)