#!/usr/bin/python3

import unittest
import json

import generate_credit_list

class Tests(unittest.TestCase):
	def setUp(self):
		with open('./test_data.json') as file:
			json_string = file.read()
			self.test_data = json.loads(json_string)


	def test_test(self):
		debts = generate_credit_list.generate_credit_list(self.test_data)
		self.assertEqual(len(debts), 0)

if (__name__ == '__main__'):
	unittest.main()