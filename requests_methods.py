import requests
import json

import service

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
		service.printt('Something went wrong when fetching history: {}'.format(response.text))
		raise SystemExit(0)

	return response.json()