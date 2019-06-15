import os
from pathlib import Path

from pretf.tests import TerraformTestCase

expected_iam_default_output = {
    "user_name": {
        "sensitive": False,
        "type": "string",
        "value": "pretf-workspaces-default",
    }
}

expected_iam_prod_output = {
    "user_name": {
        "sensitive": False,
        "type": "string",
        "value": "pretf-workspaces-prod",
    }
}

expected_vpc_default_output = {
    "vpc_id": {"sensitive": False, "type": "string", "value": "vpc-04bbd3a76beb3bfd2"}
}


expected_vpc_prod_output = {
    "vpc_id": {"sensitive": False, "type": "string", "value": "vpc-07525549c07b7eaef"}
}


class TestWorkspaces(TerraformTestCase):
    def test_output(self):
        top = Path(__file__).parent.parent
        tests = {
            ("iam", "default"): expected_iam_default_output,
            ("iam", "prod"): expected_iam_prod_output,
            ("vpc", "default"): expected_vpc_default_output,
            ("vpc", "prod"): expected_vpc_prod_output,
        }
        for ((stack, workspace), expected) in sorted(tests.items()):
            with self.subTest(f"{stack}/{workspace}"):
                os.chdir(top / "stacks" / stack)
                # self.terraform_init()
                self.terraform("workspace", "select", workspace)
                # self.terraform_apply()
                output = self.terraform_output_json()
                self.assertEqual(expected, output)
