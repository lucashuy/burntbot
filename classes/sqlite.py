import sqlite3
import datetime

from utilities.transaction_parser import determine_shaketag, determine_swap_amnt, determine_userid
from utilities.datetime import epoch_to_datetime, get_paddle_datetime, string_to_datetime

class SQLite:
	def __init__(self):
		self._conn = sqlite3.connect('./.persistence.sqlite3')
		self._db = self._conn.cursor()

		self._db.execute('PRAGMA journal_mode = WAL;')
		self._db.execute('PRAGMA foreign_keys = ON;')

		self._init_tables()

		if (self.get_key_value('poll_rate') == None): self.upsert_key_value('poll_rate', 10)
		self._conn.commit()

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
				swap_epoch INTEGER NOT NULL,
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
				ignore_until_epoch INTEGER,
				warning_hash TEXT
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

	def upsert_shaketag(self, user_id: str, shaketag: str, epoch: int):
		'''
		Adds a shaketag to the database if it does not exist, otherwise update the last swap epoch timestamp
		'''

		self._db.execute('INSERT INTO shaketags (user_id, shaketag, last_swap_epoch) VALUES (?, ?, ?) ON CONFLICT (user_id, shaketag) DO UPDATE SET last_swap_epoch = ? WHERE (user_id = ? AND shaketag = ?) AND last_swap_epoch < ?', (user_id, shaketag, epoch, epoch, user_id, shaketag, epoch));

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

		self._db.execute('INSERT INTO transactions (user_id, shaketag, transaction_id, swap_epoch, note, amount) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (transaction_id) DO NOTHING', (user_id, shaketag, transaction_id, epoch, note, amount))

	def add_list(self, shaketag: str):
		'''
		Adds a shaketag to the list, does nothing if it already exists
		'''

		# make new list entry with incrementing positions
		# if no rows (IFNULL), then set pos == 0, otherwise MAX + 1
		self._db.execute(
			'''
			INSERT INTO list (shaketag, pos, ignore_until_epoch, warning_hash) VALUES (
				?,
				(SELECT IFNULL(MAX(pos), -1) + 1 FROM list),
				NULL,
				NULL
			) ON CONFLICT DO NOTHING
			''', (shaketag,))

	def update_list_position(self, shaketag: str, pos: int):
		'''
		Updates the shaketag's position in the list, doing nothing if it the position is already taken
		'''

		self._db.execute('UPDATE list SET pos = ? WHERE shaketag = ? ON CONFLICT DO NOTHING', (pos, shaketag))

	def update_list_ignore(self, shaketag: str, ignore_epoch):
		'''
		Updates the shaketag's "ignore" value in the list. This is used to delay automated sending to the list
		'''

		self._db.execute('UPDATE list SET ignore_until_epoch = ? WHERE shaketag = ?', (ignore_epoch, shaketag))

	def update_list_warning(self, shaketag: str, warning_hash):
		'''
		Updates the shaketag's warning hash value in the list. This is used to ignore warnings from the swapper database
		'''

		self._db.execute('UPDATE list SET warning_hash = ? WHERE shaketag = ?', (warning_hash, shaketag))

	def delete_list(self, shaketag: str):
		'''
		Delete a shaketag from the list
		'''

		self._db.execute('DELETE FROM list WHERE shaketag = ?', (shaketag,))

	def upsert_blacklist(self, shaketag: str, amount: float):
		'''
		Insert a blacklist amount if it does not exist, otherwise update the amount
		'''

		self._db.execute('INSERT INTO blacklist VALUES (?, ?) ON CONFLICT (shaketag) DO UPDATE SET amount = ? WHERE shaketag = ?', (shaketag, amount, amount, shaketag))

	def delete_blacklist(self, shaketag: str):
		'''
		Deletes a blacklist amount
		'''

		self._db.execute('DELETE FROM list WHERE shaketag = ?', (shaketag,))

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
		Updates the shaketag's "ignore" value in the list
		'''

		self._db.execute('INSERT INTO kv VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = ? WHERE key = ?', (key, value, value, key))

	def get_paddle_swappers(self) -> int:
		'''
		Gets the amount of swappers since paddle introduction

		@returns A positive integer in the range `[0, +inf)`
		'''

		self._db.execute('SELECT COUNT(*) FROM (SELECT MAX(last_swap_epoch) FROM shaketags WHERE last_swap_epoch >= ? GROUP BY user_id)', (get_paddle_datetime().timestamp(),))
		return self._db.fetchone()[0]

	def get_credits(self) -> list:
		'''
		Gets a list of people that have positive balances

		@returns A list of tuples in the format `[(shaketag: str, amount: float), ...]`
		'''

		self._db.execute('SELECT * FROM (SELECT shaketag, ROUND(TOTAL(amount), 2) balance FROM transactions WHERE note IS NOT "no return" GROUP BY shaketag) WHERE balance > 0')
		return self._db.fetchall()

	def get_last_transaction_epoch(self) -> datetime.datetime:
		'''
		Gets a `datetime` object of the last (most recent) transaction saved

		@returns A `datetime` object or `None` if none exists
		'''

		self._db.execute('SELECT MAX(last_swap_epoch) FROM shaketags')
		
		result = self._db.fetchone()[0]
		if (not result == None): result = epoch_to_datetime(result)

		return result

	def commit(self):
		self._conn.commit()

	def close(self):
		self._db.close()
		self._conn.close()