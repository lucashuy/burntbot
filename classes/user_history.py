class UserHistory():
	def __init__(self, timestamp: str, swap: float):
		self.timestamp = timestamp
		self.swap = swap

	def update_timestamp(self, timestamp: str):
		self.timestamp = timestamp

	def get_timestamp(self):
		return self.timestamp

	def adjust_swap(self, swap: float):
		self.swap = self.swap + swap

	def get_swap(self):
		return self.swap