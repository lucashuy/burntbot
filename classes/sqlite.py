import sqlite3
import datetime

from utilities.transaction_parser import determine_shaketag, determine_swap_amnt, determine_userid
from utilities.datetime import epoch_to_datetime, get_paddle_datetime, string_to_datetime, get_reset_datetime

class SQLite:
	def __init__(self):
		self._conn = sqlite3.connect('./.persistence.sqlite3')
		self._db = self._conn.cursor()

		self._db.execute('PRAGMA journal_mode = WAL;')
		self._db.execute('PRAGMA foreign_keys = ON;')

		self._init_tables()

		if (self.get_key_value('poll_rate') == None): self.upsert_key_value('poll_rate', 10)
		self._conn.commit()

	########################################3
	#	sql management
	#
	def commit(self):
		self._conn.commit()

	def close(self):
		self._db.close()
		self._conn.close()

	def _init_tables(self):
		self._db.execute(
			'''
			CREATE TABLE IF NOT EXISTS shaketags (
				user_id TEXT NOT NULL,
				shaketag TEXT NOT NULL,
				last_swap_epoch INTEGER NOT NULL,
				PRIMARY KEY (user_id, shaketag)
			)
			'''
		)

		self._db.execute(
			'''
			CREATE TABLE IF NOT EXISTS transactions (
				user_id TEXT NOT NULL,
				shaketag TEXT NOT NULL,
				transaction_id TEXT NOT NULL PRIMARY KEY,
				created_at INTEGER NOT NULL,
				note TEXT,
				amount REAL NOT NULL,
				FOREIGN KEY (user_id, shaketag) REFERENCES shaketags(user_id, shaketag) ON DELETE CASCADE
			)
			'''
		)

		self._db.execute(
			'''
			CREATE TABLE IF NOT EXISTS list (
				shaketag TEXT NOT NULL UNIQUE,
				pos INTEGER NOT NULL,
				warning TEXT
			)
			'''
		)

		self._db.execute(
			'''
			CREATE TABLE IF NOT EXISTS blacklist (
				shaketag TEXT NOT NULL UNIQUE,
				amount FLOAT NOT NULL
			)
			'''
		)

		self._db.execute(
			'''
			CREATE TABLE IF NOT EXISTS kv (
				key TEXT NOT NULL UNIQUE,
				value BLOB
			)
			'''
		)

	########################################3
	#	table: shaketags
	#
	def upsert_shaketag(self, user_id: str, shaketag: str, epoch: int):
		'''
		Adds a shaketag to the database if it does not exist, otherwise update the last swap epoch timestamp
		'''

		self._db.execute('INSERT INTO shaketags (user_id, shaketag, last_swap_epoch) VALUES (?, ?, ?) ON CONFLICT (user_id, shaketag) DO UPDATE SET last_swap_epoch = ? WHERE (user_id = ? AND shaketag = ?) AND last_swap_epoch < ?', (user_id, shaketag, epoch, epoch, user_id, shaketag, epoch));
	
	def get_paddle_swappers(self) -> int:
		'''
		Gets the amount of swappers since paddle introduction

		@returns A positive integer in the range `[0, +inf)`
		'''

		self._db.execute('SELECT COUNT(*) FROM (SELECT MAX(last_swap_epoch) FROM shaketags WHERE last_swap_epoch >= ? GROUP BY user_id)', (get_paddle_datetime().timestamp(),))
		return self._db.fetchone()[0]
	
	def get_last_transaction_epoch(self) -> datetime.datetime:
		'''
		Gets a `datetime` object of the last (most recent) transaction saved

		@returns A `datetime` object or `None` if none exists
		'''

		self._db.execute('SELECT MAX(last_swap_epoch) FROM shaketags')
		
		result = self._db.fetchone()[0]
		if (not result == None): result = epoch_to_datetime(result)

		return result

	def get_shaketag_info(self, shaketag: str):
		'''
		Gets the user's info from the `shaketags` table

		@param `shaketag` The shaketag of the user with leading `@`

		@returns `None` if there is no such shaketag, otherwise returns `tuple`
		'''

		self._db.execute('SELECT * FROM shaketags WHERE shaketag = ? LIMIT 1', (shaketag,))

		# return tuple if exists
		result = self._db.fetchone()
		return result

	########################################3
	#	table: transactions
	#
	def add_transcation(self, transaction: dict):
		'''
		Adds a transaction to the database, does nothing if it already exists
		'''

		# local data
		user_id = determine_userid(transaction)
		shaketag = determine_shaketag(transaction)
		transaction_id = transaction['transactionId']
		epoch = string_to_datetime(transaction['timestamp']).timestamp()
		note = transaction['note']
		amount = determine_swap_amnt(transaction)

		self._db.execute('INSERT INTO transactions (user_id, shaketag, transaction_id, created_at, note, amount) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (transaction_id) DO NOTHING', (user_id, shaketag, transaction_id, epoch, note, amount))

	def get_credits(self) -> list:
		'''
		Gets a list of people that have positive balances (waiting to send back)

		@returns A list of tuples in the format `[(shaketag: str, amount: float, timestamp: float), ...]`
		'''

		self._db.execute('''
			SELECT * FROM (
				SELECT shaketag, ROUND(TOTAL(amount), 2) balance FROM (
					SELECT shaketag, amount FROM transactions WHERE note IS NOT "no return"
						UNION ALL
					SELECT shaketag, amount FROM blacklist
				) GROUP BY shaketag
			) WHERE balance > 0
		''')
		return self._db.fetchall()

	def get_debits(self) -> list:
		'''
		Gets a list of people that have negative balances (waiting for swap back)

		@returns A list of tuples in the format `[(shaketag: str, amount: float, timestamp: float), ...]`
		'''

		self._db.execute('''
			SELECT * FROM (
				SELECT shaketag, ROUND(TOTAL(amount), 2) balance FROM (
					SELECT shaketag, amount FROM transactions WHERE note IS NOT "no return"
						UNION ALL
					SELECT shaketag, amount FROM blacklist
				) GROUP BY shaketag
			) WHERE balance < 0
		''')
		return self._db.fetchall()

	def have_swapped(self, shaketag: str) -> bool:
		'''
		Checks if we have swapped with this user today

		@param `shaketag` The shaketag of the user with the leading `@`

		@returns `True` if swapped
		'''

		self._db.execute('SELECT EXISTS(SELECT 1 FROM transactions WHERE shaketag = ? AND created_at >= ? AND amount <= -5.0 LIMIT 1)', (shaketag, get_reset_datetime().timestamp()))
		return self._db.fetchone()[0]
		
	########################################3
	#	table: list
	#
	def add_list(self, shaketag: str):
		'''
		Adds a shaketag to the list, does nothing if it already exists
		'''

		# make new list entry with incrementing positions
		# if no rows (IFNULL), then set pos == 0, otherwise MAX + 1
		self._db.execute(
			'''
			INSERT INTO list (shaketag, pos, warning) VALUES (
				?,
				(SELECT IFNULL(MAX(pos), -1) + 1 FROM list),
				NULL
			) ON CONFLICT DO NOTHING
			''', (shaketag,))

	def update_list_position(self, shaketag: str, pos: int):
		'''
		Updates the shaketag's position in the list, doing nothing if it the position is already taken
		'''

		self._db.execute('UPDATE list SET pos = ? WHERE shaketag = ?', (pos, shaketag))

	def update_list_warning(self, shaketag: str, warning):
		'''
		Updates the shaketag's warning hash value in the list. This is used to ignore warnings from the swapper database
		'''

		self._db.execute('UPDATE list SET warning = ? WHERE shaketag = ?', (warning, shaketag))

	def delete_from_list(self, shaketag: str):
		'''
		Delete a shaketag from the list
		'''

		self._db.execute('DELETE FROM list WHERE shaketag = ?', (shaketag,))

	def get_list(self):
		'''
		Gets the entire list
		'''

		self._db.execute('SELECT * FROM list ORDER BY pos ASC')
		return self._db.fetchall()

	def get_list_shaketag(self, shaketag: str) -> tuple:
		'''
		Gets a specific row from the list

		@param `shaketag` A shaketag with the leading `@`
		
		@returns The row as outlined in the table schema
		'''

		self._db.execute('SELECT * FROM list WHERE shaketag = ?', (shaketag,))
		return self._db.fetchone()

	def clear_list(self):
		'''
		Wipes the entire list
		'''

		self._db.execute('DELETE FROM list')

	########################################3
	#	table: blacklist
	#
	def upsert_blacklist(self, shaketag: str, amount: float):
		'''
		Insert a blacklist amount if it does not exist, otherwise update the amount
		'''

		self._db.execute('INSERT INTO blacklist VALUES (?, ?) ON CONFLICT (shaketag) DO UPDATE SET amount = ? WHERE shaketag = ?', (shaketag, amount, amount, shaketag))

	def delete_blacklist(self, shaketag: str):
		'''
		Deletes a blacklist amount
		'''

		self._db.execute('DELETE FROM blacklist WHERE shaketag = ?', (shaketag,))

	def get_blacklist(self) -> list:
		'''
		Gets all blacklisted users

		@returns A `list` of blacklisted users and their amounts
		'''

		self._db.execute('SELECT * FROM blacklist')
		return self._db.fetchall()

	########################################3
	#	table: kv
	#
	def get_key_value(self, key: str, default_value = None):
		'''
		Get a key/value pair

		@param `key` The key
		@param `default_value` (Optional) The default value to return if no such key exists

		@returns value if key exists, otherwise returns `default_value
		'''

		self._db.execute('SELECT value FROM kv WHERE key = ?', (key,))

		result = self._db.fetchone()

		if (result == None):
			return default_value
		else:
			return result[0]

	def upsert_key_value(self, key: str, value):
		'''
		Updates the key/value pair in the database

		@param `key` The key
		@param `value` The value
		'''

		self._db.execute('INSERT INTO kv VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = ? WHERE key = ?', (key, value, value, key))