import unittest

from pretf import parser

apply_stdout_strings = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

one = one
two =
three = three
"""

apply_stdout_numbers = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

one = 1
two = 22
three = 3.3
four = 4 string
"""

apply_stdout_bools = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

one = true
two = false
three = true string
four = false string
"""


class TestParser(unittest.TestCase):
    def test_apply_outputs_parser(self):

        outputs = parser.parse_apply_outputs(apply_stdout_strings)

        self.assertEqual(outputs, {"one": "one", "two": "", "three": "three"})

        outputs = parser.parse_apply_outputs(apply_stdout_numbers)

        self.assertEqual(
            outputs, {"one": 1, "two": 22, "three": 3.3, "four": "4 string"}
        )

        outputs = parser.parse_apply_outputs(apply_stdout_bools)

        self.assertEqual(
            outputs,
            {"one": True, "two": False, "three": "true string", "four": "false string"},
        )
