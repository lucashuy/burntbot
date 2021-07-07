bot_note = ''
bot_poll_rate = 10

# create constants for API endpoints
_host = 'https://api.shakepay.com/'
endpoint_wallet = _host + 'wallets'
endpoint_history = _host + 'transactions/history'
endpoint_swap = _host + 'transactions'
endpoint_authenticate = _host + 'authentication'
endpoint_users = _host + 'users'
endpoint_waitlist = _host + 'card/waitlist'
endpoint_shaking_sats = _host + 'shaking-sats'

# headers required for requests
headers = {'User-Agent': 'Shakepay App v1.6.100 (16100) on samsung SM-G930W8 (Android 8.0.0)'}

# wallet id
wallet_id = ''

# our shaketag
shaketag = ''

# waitlist specific data (cache header, position, etc)
waitlist_etag = None
waitlist_position = 0
waitlist_points = 0
waitlist_paddles = []

# trading history hash table
bot_history = {}

# bot specific flags
bot_flags = {
	'listen': False,
	'verbose': False
}

# version of bot for update checking
version = '0.0.0'

# webui host and port
webui_host = '0.0.0.0'
webui_port = '5000'

# blacklist and balance
bot_blacklist = {}

# auto sendlist
bot_send_list = {}

# check shaketag against database before returning
bot_return_check = False

# whether or not to enable auto shake
shaking_sats_enabled = False

# whether or not to broadcast bot alive status to API
heart_beat_enabled = False
heart_beat_points = False
heart_beat_swaps = False
heart_beat_position = False

# note for list sends
list_note = ''

######################################
# state specific variables
# not saved

# bot state
# 0 = restarting
# 1 = alive
bot_state = 0

# shakepay user id
user_id = ''