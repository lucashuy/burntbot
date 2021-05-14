#!/usr/bin/python3

import unittest
import json

import filter_transactions

class Tests(unittest.TestCase):
	def setUp(self):
		with open('./test_data_fetch.json') as file:
			self.test_data_fetch_raw = file.read()

		with open('./test_data_history.json') as file:
			self.test_data_history_raw = file.read()

	def test_even(self):
		history = json.loads(self.test_data_history_raw)
		
		send_list = filter_transactions.filter_transactions(json.loads(self.test_data_fetch_raw), history)

		self.assertEqual(len(send_list), 0)

	# this test will fail on python versions < 3.6 since in lesser versions dicts are not ordered
	def test_single_owe(self):
		history = json.loads(self.test_data_history_raw)

		
		data = json.loads(self.test_data_fetch_raw)
		del data['data'][0]

		send_list = filter_transactions.filter_transactions(data, history)
		
		self.assertNotEqual(len(send_list), 0)

		debt = next(iter(send_list))
		self.assertEqual(send_list[debt]['transactionId'], 'TI_DICFJ3C5YOZHS45')

if (__name__ == '__main__'):
	unittest.main()