import unittest

from pretf import parser

apply_stdout = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

lambda_role_combination_1 = lambda_role_combination_1
lambda_role_combination_2 = lambda_role_combination_2
"""

apply_empty_string_stdout = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

lambda_role_combination_1 = lambda_role_combination_1
lambda_role_combination_2 =
lambda_role_combination_3 = lambda_role_combination_3
"""


class TestParser(unittest.TestCase):
    def test_apply_outputs_parser(self):

        outputs = parser.parse_apply_outputs(apply_stdout)

        self.assertEqual(
            outputs,
            {
                "lambda_role_combination_1": "lambda_role_combination_1",
                "lambda_role_combination_2": "lambda_role_combination_2",
            },
        )

        outputs = parser.parse_apply_outputs(apply_empty_string_stdout)

        self.assertEqual(
            outputs,
            {
                "lambda_role_combination_1": "lambda_role_combination_1",
                "lambda_role_combination_2": "",
                "lambda_role_combination_3": "lambda_role_combination_3",
            },
        )
