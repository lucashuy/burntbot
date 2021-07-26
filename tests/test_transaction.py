import unittest
import os
import json

import globals

from utilities.transaction_parser import get_swaps, populate_history

class TransactionTest(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.data = []

		files = next(os.walk('./tests/data/', (None, None, [])))[2]
		files.sort()
		
		for filename in files:
			with open(f'./tests/data/{filename}') as f:
				self.data.append(json.loads(f.read())['data'])

	def setUp(self):
		globals.bot_history = {}

		for data in self.data:
			populate_history(data)

	def test_history_clean(self):
		for _, history in globals.bot_history.items():
			self.assertEqual(history.get_swap(), 0.)

	def test_history_num_users(self):
		self.assertEqual(557, len(globals.bot_history))

	def test_history_extra_credit(self):
		populate_history([{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 5, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}])

		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), 5.)

	def test_history_extra_debit(self):
		populate_history([{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}])

		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), -5.)

	def test_pull_completed_swap(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}},
			{"transactionId": "TI_ELKA8TJUA5VDT30", "createdAt": "2021-07-21T19:34:19.323Z", "timestamp": "2021-07-21T19:34:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 5, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 0)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), 0.)

	def test_pull_credit(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT30", "createdAt": "2021-07-21T19:34:19.323Z", "timestamp": "2021-07-21T19:34:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 5, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 1)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), 5.)

	def test_pull_debit(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 0)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), -5.)

	def test_pull_double_debit(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}},
			{"transactionId": "TI_ELKA8TJUA5VDT30", "createdAt": "2021-07-21T19:34:19.323Z", "timestamp": "2021-07-21T19:34:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 0)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), -10.)

	def test_pull_double_credit(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 5, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}},
			{"transactionId": "TI_ELKA8TJUA5VDT30", "createdAt": "2021-07-21T19:34:19.323Z", "timestamp": "2021-07-21T19:34:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 5, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 1)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), 10.)

	def test_pull_dupe_credit(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 5, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}},
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 5, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 1)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), 5.)

	def test_pull_dupe_debit(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}},
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 0)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), -5.)

	def test_pull_partial_credit(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "", "direction": "credit", "currency": "CAD", "amount": 7, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}},
			{"transactionId": "TI_ELKA8TJUA5VDT30", "createdAt": "2021-07-21T19:34:19.323Z", "timestamp": "2021-07-21T19:34:19.323Z", "note": "", "direction": "debit", "currency": "CAD", "amount": 5, "type": "peer", "to": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 1)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), 2.)

	def test_pull_no_return(self):
		list = get_swaps([
			{"transactionId": "TI_ELKA8TJUA5VDT29", "createdAt": "2021-07-21T19:33:19.323Z", "timestamp": "2021-07-21T19:33:19.323Z", "note": "no return", "direction": "credit", "currency": "CAD", "amount": 7, "type": "peer", "from": {"label": "-hidden-", "id": "US_XW5DC4SKPCAYZFU"}}
		])

		self.assertEqual(len(list), 0)
		self.assertEqual(globals.bot_history['US_XW5DC4SKPCAYZFU'].get_swap(), 0.)

	def test_pull_empty(self):
		list = get_swaps([])

		self.assertEqual(len(list), 0)

		for _, history in globals.bot_history.items():
			self.assertEqual(history.get_swap(), 0.)