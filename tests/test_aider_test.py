import unittest
from aider_test import hello

class TestAiderTest(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello(), "Hello from Aider")

if __name__ == "__main__":
    unittest.main()
