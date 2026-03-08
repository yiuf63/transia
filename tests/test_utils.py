import unittest
from transia.standalone_utils import uid, trim

class TestUtils(unittest.TestCase):
    def test_uid(self):
        self.assertEqual(uid("test"), uid("test"))
        self.assertNotEqual(uid("test1"), uid("test2"))

    def test_trim(self):
        self.assertEqual(trim("  hello  world  "), "hello world")
        self.assertEqual(trim("hello\u00a0world"), "hello world")
        self.assertEqual(trim("hello\ufeffworld"), "helloworld")

    def test_uid_multiple_args(self):
        self.assertEqual(uid("a", "b"), uid("a", "b"))
        self.assertNotEqual(uid("a", "b"), uid("b", "a"))
