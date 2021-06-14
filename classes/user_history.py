class UserHistory():
	def __init__(self, shaketag: str, timestamp: str, swap: float):
		self.shaketag = shaketag
		self.timestamp = timestamp
		self.swap = swap
		self.previous_transactions = {}

	def update_timestamp(self, timestamp: str):
		self.timestamp = timestamp

	def get_timestamp(self) -> str:
		return self.timestamp

	def adjust_swap(self, swap: float):
		self.swap = float(f'{self.swap + swap:.2f}')

	def get_swap(self) -> float:
		return self.swap

	def update_shaketag(self, shaketag: str):
		self.shaketag = shaketag

	def get_shaketag(self) -> str:
		return self.shaketag

	def add_prev_transaction(self, transaction: dict):
		self.previous_transactions[transaction['transactionId']] = transaction

	def transaction_exists(self, trans_id: str) -> bool:
		return trans_id in self.previous_transactions