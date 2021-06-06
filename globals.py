note = ''
poll_rate = 10

# create constants for API endpoints
_host = 'https://api.shakepay.com/'
endpoint_wallet = _host + 'wallets'
endpoint_history = _host + 'transactions/history'
endpoint_swap = _host + 'transactions'
endpoint_authenticate = _host + 'authentication'

# headers required for requests
headers = {'User-Agent': 'Shakepay App v1.6.100 (16100) on samsung SM-G930W8 (Android 8.0.0)'}

# CAD wallet ID
wallet_id = ''

# trading history hash table
history = {}

flags = {
	'listen': False,
	'verbose': False
}

version = '0.0.0'