import unittest

from classes.version import Version

class VersionTest(unittest.TestCase):
	def test_constructor_valid(self):
		v = Version('1.2.3')

		self.assertEqual(v.major, 1)
		self.assertEqual(v.minor, 2)
		self.assertEqual(v.patch, 3)
		
	def test_constructor_invalid(self):
		v = Version('1.2.3.4')

		self.assertEqual(v.major, 0)
		self.assertEqual(v.minor, 0)
		self.assertEqual(v.patch, 0)

	def test_lt(self):
		# everything lower
		v1 = Version('1.2.3')
		v2 = Version('2.3.4')

		self.assertTrue(v1 < v2)

		# everything but major lower
		v1 = Version('1.2.3')
		v2 = Version('2.1.1')

		self.assertTrue(v1 < v2)

		# everything but minor lower
		v1 = Version('1.2.3')
		v2 = Version('2.1.4')

		self.assertTrue(v1 < v2)

		# everything but patch lower
		v1 = Version('1.2.3')
		v2 = Version('2.3.1')

		self.assertTrue(v1 < v2)

		# not larger
		v1 = Version('2.3.4')
		v2 = Version('1.1.1')

		self.assertFalse(v1 < v2)

	def test_le(self):
		v1 = Version('1.0.0')
		v2 = Version('1.1.1')

		self.assertTrue(v1 <= v2)

		v1 = Version('1.1.1')
		v2 = Version('1.1.1')

		self.assertTrue(v1 <= v2)

		v1 = Version('1.1.2')
		v2 = Version('1.1.1')

		self.assertFalse(v1 <= v2)

	def test_gt(self):
		v1 = Version('1.2.3')
		v2 = Version('1.1.1')

		self.assertTrue(v1 > v2)

		v1 = Version('2.0.0')
		v2 = Version('1.1.1')

		self.assertTrue(v1 > v2)

		v1 = Version('1.0.3')
		v2 = Version('1.1.1')

		self.assertFalse(v1 > v2)

		v1 = Version('1.1.1')
		v2 = Version('1.1.1')

		self.assertFalse(v1 > v2)

	def test_ge(self):
		v1 = Version('1.1.1')
		v2 = Version('1.1.1')

		self.assertTrue(v1 >= v2)

		v1 = Version('1.1.2')
		v2 = Version('1.1.1')

		self.assertTrue(v1 >= v2)

		v1 = Version('2.0.0')
		v2 = Version('1.1.1')

		self.assertTrue(v1 >= v2)

		v1 = Version('1.0.2')
		v2 = Version('1.1.1')

		self.assertFalse(v1 >= v2)

		v1 = Version('0.0.2')
		v2 = Version('1.1.1')

		self.assertFalse(v1 >= v2)

	def test_eq(self):
		v1 = Version('1.2.3')
		v2 = Version('1.2.3')

		self.assertEqual(v1, v2)

		v1 = Version('0.1.2')
		v2 = Version('1.2.3')

		self.assertNotEqual(v1, v2)

	def test_ne(self):
		v1 = Version('1.2.1')
		v2 = Version('1.2.3')

		self.assertNotEqual(v1, v2)

		v1 = Version('1.1.3')
		v2 = Version('1.2.3')

		self.assertNotEqual(v1, v2)

		v1 = Version('1.2.3')
		v2 = Version('0.2.3')

		self.assertNotEqual(v1, v2)