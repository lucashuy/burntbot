note = ''
poll_rate = 10

# create constants for API endpoints
_host = 'https://api.shakepay.com/'
endpoint_wallet = _host + 'wallets'
endpoint_history = _host + 'transactions/history'
endpoint_swap = _host + 'transactions'
endpoint_authenticate = _host + 'authentication'
endpoint_users = _host + 'users'
endpoint_waitlist = _host + 'card/waitlist'

# headers required for requests
headers = {'User-Agent': 'Shakepay App v1.6.100 (16100) on samsung SM-G930W8 (Android 8.0.0)'}

# CAD wallet ID
wallet_id = ''

# our shaketag
shaketag = ''

# waitlist specific data (cache header, position, etc)
waitlist_etag = None
waitlist_position = 0
waitlist_points = 0
waitlist_paddles = []

# trading history hash table
history = {}

# bot specific flags
flags = {
	'listen': False,
	'verbose': False
}

# version of bot for update checking
version = '0.0.0'

# webui host and port
webui_host = '127.0.0.1'
webui_port = '5000'