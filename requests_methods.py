import requests
import json

"""
Logins in to Shakepay using a 2FA code (from CLI) and returns the JWT
"""
def login(username, password, url, base_headers):
	# copy headers so that we can add content type
	local_headers = base_headers.copy()
	local_headers['Content-Type'] = 'application/json'

	# create JSON body for login (pre 2FA)
	body = json.dumps({
		'password': password,
		'username': username,
		'totpType': 'sms',
		'strategy': 'local'
	})

	print('+ Logging onto Shakepay')
	
	response_non_2fa = requests.post(url, headers = local_headers, data = body)
	
	# make sure we have 2xx status
	if (not response_non_2fa.ok):
		print('! Something went wrong when authenticating (pre 2FA): {}'.format(response_non_2fa.text))
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
	response_2fa = requests.post(url, headers = local_headers, data = body)

	if (not response_2fa.ok):
		print('! Something went wrong when authenticating (2FA): {}'.format(response_non_2fa.text))
		raise SystemExit(0)

	return response_2fa.json()['accessToken']

"""
Returns a history of CAD transactions
"""
def history(url, base_headers, token, body):
	# copy headers
	local_headers = base_headers.copy()
	local_headers['Content-Type'] = 'application/json'
	local_headers['Authorization'] = token

	response = requests.post(url, headers = local_headers, data = json.dumps(body))
	
	# make sure we have 2xx status
	if (not response.ok):
		print('! Something went wrong when fetching history: {}'.format(response.text))
		raise SystemExit(0)

	return response.json()