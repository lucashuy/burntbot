# headers required for requests (populated in start.py)
headers = {
	'Accept-Encoding': 'gzip, deflate'
}

# wallet id
wallet_id = ''

# our shaketag
shaketag = ''

# waitlist specific data (cache header, position, etc)
waitlist_etag = None
waitlist_position = 0
waitlist_points = 0
waitlist_paddles = []
waitlist_swaps = 0
waitlist_last_check = 0

# bot specific flags
bot_flags = {
	'listen': False,
	'verbose': False,
	'demo': False
}

# version of bot for update checking
version = None

# webui host and port
webui_host = '0.0.0.0'
webui_port = '5000'
