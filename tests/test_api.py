import unittest

from pretf.api import block


class TestAPI(unittest.TestCase):
    def test_provider_alias(self):
        default = block("provider", "aws", {"alias": "nonprod"})
        self.assertEqual(str(default.alias), "aws.nonprod")

    def test_provider_alias_default(self):
        default = block("provider", "aws", {})
        self.assertEqual(str(default.alias), "aws.default")

    def test_variable(self):
        one = block("variable", "one", {})
        self.assertEqual(str(one), "${var.one}")
