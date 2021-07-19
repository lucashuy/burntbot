class Version:
	def __init__(self, version: str):
		explode = version.split('.')

		# basic input validation
		if (len(explode) == 3):
			self.major = int(explode[0])
			self.minor = int(explode[1])
			self.patch = int(explode[2])
		else:
			self.major = 0
			self.minor = 0
			self.patch = 0

	def to_string(self) -> str:
		return f'{self.major}.{self.minor}.{self.patch}'

	def __repr__(self) -> str:
		return self.to_string()

	def __str__(self) -> str:
		return self.to_string()

	def __lt__(self, other) -> bool:
		if (self.major < other.major): return True

		if (self.major == other.major):
			if (self.minor < other.minor): return True

			if (self.minor == other.minor):
				if (self.patch < other.patch): return True

		return False

	def __le__(self, other) -> bool:
		if (self.major < other.major): return True

		if (self.major == other.major):
			if (self.minor < other.minor): return True

			if (self.minor == other.minor):
				if (self.patch <= other.patch): return True

		return False

	def __eq__(self, other) -> bool:
		return (self.major == other.major) and (self.minor == other.minor) and (self.patch == other.patch)

	def __ne__(self, other) -> bool:
		return not self == other

	def __gt__(self, other) -> bool:
		if (self.major > other.major): return True

		if (self.major == other.major):
			if (self.minor > other.minor): return True

			if (self.minor == other.minor):
				if (self.patch > other.patch): return True

		return False

	def __ge__(self, other) -> bool:
		if (self.major > other.major): return True

		if (self.major == other.major):
			if (self.minor > other.minor): return True

			if (self.minor == other.minor):
				if (self.patch >= other.patch): return True

		return False
