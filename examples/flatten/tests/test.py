import os
from pathlib import Path

from pretf.tests import TerraformTestCase

expected_iam_dev_output = {
    "user_name": {"sensitive": False, "type": "string", "value": "pretf-flatten-dev"}
}

expected_iam_prod_output = {
    "user_name": {"sensitive": False, "type": "string", "value": "pretf-flatten-prod"}
}

expected_vpc_dev_output = {
    "vpc_id": {"sensitive": False, "type": "string", "value": "vpc-0bbc0e94928ec4523"}
}


expected_vpc_prod_output = {
    "vpc_id": {"sensitive": False, "type": "string", "value": "vpc-0df4133123c11575b"}
}


class TestFlatten(TerraformTestCase):
    def test_output(self):
        top = Path(__file__).parent.parent
        tests = {
            ("iam", "dev"): expected_iam_dev_output,
            ("iam", "prod"): expected_iam_prod_output,
            ("vpc", "dev"): expected_vpc_dev_output,
            ("vpc", "prod"): expected_vpc_prod_output,
        }
        for ((stack, env), expected) in sorted(tests.items()):
            with self.subTest(f"{stack}/{env}"):
                os.chdir(top / "stacks" / stack / env)
                # self.terraform_init()
                self.terraform_apply()
                output = self.terraform_output_json()
                self.assertEqual(expected, output)
