from pretf.tests import Any, TerraformTestCase

expected_iam_dev_output = {
    "user_name": {"sensitive": False, "type": "string", "value": "pretf-flatten-dev"}
}

expected_iam_prod_output = {
    "user_name": {"sensitive": False, "type": "string", "value": "pretf-flatten-prod"}
}

expected_vpc_dev_output = {
    "vpc_id": {"sensitive": False, "type": "string", "value": Any()}
}


expected_vpc_prod_output = {
    "vpc_id": {"sensitive": False, "type": "string", "value": Any()}
}


class TestFlatten(TerraformTestCase):
    def test_output(self):
        tests = {
            ("iam", "dev"): expected_iam_dev_output,
            ("iam", "prod"): expected_iam_prod_output,
            ("vpc", "dev"): expected_vpc_dev_output,
            ("vpc", "prod"): expected_vpc_prod_output,
        }
        for ((stack, env), expected) in sorted(tests.items()):
            with self.subTest(f"{stack}/{env}"):

                # Change to the Terraform project directory,
                # relative to this test file rather than where
                # the unittest command is running from.
                self.chdir(f"../stacks/{stack}/{env}")

                try:

                    # Run terraform init and apply to create resources.
                    self.terraform_init()
                    self.terraform_apply()

                    # Run terraform output and check the results.
                    output = self.terraform_output_json()
                    self.assertEqual(expected, output)

                finally:

                    # Run terraform destroy to clean up resources.
                    self.terraform_destroy()
