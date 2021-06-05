import json
import sys
import os

PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
FILE_NAME = '.persistence'
FULL_PATH = f'{PATH}/{FILE_NAME}'

def read_persistence() -> dict:
	with open(FULL_PATH) as file:
		persistence = json.loads(file.readline())

	return persistence or {}

def upsert_persistence(data: dict):
	read_data = {}

	# read data, even if it doesnt exist
	try:
		read_data = read_persistence()
	except: pass

	# merge read data and param data
	for key, value in data.items():
		read_data[key] = value

	# write to file
	with open(FULL_PATH, 'w') as file:
		file.write(json.dumps(read_data))