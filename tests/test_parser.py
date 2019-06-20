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

apply_numbers_stdout = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

private_sg_id = sg-0d70579dc16c2ff31
public_sg_id = sg-071862b91dc0a15f1
total_bytes = 63
total_files = 5
user_pretf_iam_user_1 = pretf-iam-user-1
user_pretf_iam_user_2 = pretf-iam-user-2
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

        outputs = parser.parse_apply_outputs(apply_numbers_stdout)

        self.assertEqual(
            outputs,
            {
                "private_sg_id": "sg-0d70579dc16c2ff31",
                "public_sg_id": "sg-071862b91dc0a15f1",
                "total_bytes": 63,
                "total_files": 5,
                "user_pretf_iam_user_1": "pretf-iam-user-1",
                "user_pretf_iam_user_2": "pretf-iam-user-2",
            },
        )
