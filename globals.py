# default values for poll rate, note, etc
NOTE = ''
POLL_RATE = 10

# create constants for API endpoints
_HOST = 'https://api.shakepay.com/'
ENDPOINT_WALLET = _HOST + 'wallets'
ENDPOINT_HISTORY = _HOST + 'transactions/history'
ENDPOINT_SWAP = _HOST + 'transactions'
ENDPOINT_AUTHENTICATE = _HOST + 'authentication'

# init required headers from .env file
HEADERS = {
	'User-Agent': 'Shakepay App v1.6.100 (16100) on samsung SM-G930W8 (Android 8.0.0)',
	'X-Device-Unique-Id': '406275726e74746f',
	'X-Device-Serial-Number': '617374657220626f74'
}

# CAD wallet ID
WALLET_ID = None

# trading history hash table
HISTORY = {}