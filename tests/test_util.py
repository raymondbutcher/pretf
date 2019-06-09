import unittest

from pretf.util import once


class TestUtil(unittest.TestCase):
    def test_once(self):

        result = []

        @once
        def append_one():
            append_one()  # recursive calls do nothing
            result.append(1)
            return True

        @once
        def append_two():
            result.append(2)
            return True

        # The first call is normal, it returns True
        self.assertEqual(append_one(), True)
        self.assertEqual(result, [1])

        # Subsequent calls do nothing and return nothing.
        self.assertEqual(append_one(), None)
        self.assertEqual(append_one(), None)
        self.assertEqual(result, [1])

        # Test that multiple functions can use the decorator.
        self.assertEqual(append_two(), True)
        self.assertEqual(result, [1, 2])
        self.assertEqual(append_two(), None)
        self.assertEqual(append_two(), None)
        self.assertEqual(result, [1, 2])

    def test_once_methods(self):
        class Append:
            def __init__(self):
                self.result = []

            @once
            def append(self, value):
                self.append(value)  # recursive calls do nothing
                self.result.append(value)
                return True

        a = Append()
        b = Append()

        self.assertEqual(a.append(1), True)
        self.assertEqual(a.append(1), None)
        self.assertEqual(a.append(1), None)

        self.assertEqual(a.result, [1])

        self.assertEqual(a.append(2), True)
        self.assertEqual(a.append(2), None)
        self.assertEqual(a.append(2), None)

        self.assertEqual(a.result, [1, 2])

        self.assertEqual(b.append(3), True)
        self.assertEqual(b.append(3), None)
        self.assertEqual(b.append(3), None)

        self.assertEqual(b.result, [3])
