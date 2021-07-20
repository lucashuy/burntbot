class UserHistory():
	def __init__(self, shaketag: str, timestamp: str, swap: float):
		self.shaketag = shaketag
		self.timestamp = timestamp
		self.swap = swap
		self.transaction_cache = {}

	def add_transaction_cache(self, transaction_id: str):
		self.transaction_cache[transaction_id] = 1

	def is_transaction_cached(self, transaction_id: str) -> bool:
		return transaction_id in self.transaction_cache

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