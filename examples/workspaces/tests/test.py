from pretf.tests import Any, TerraformTestCase

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
    "vpc_id": {"sensitive": False, "type": "string", "value": Any()}
}


expected_vpc_prod_output = {
    "vpc_id": {"sensitive": False, "type": "string", "value": Any()}
}


class TestWorkspaces(TerraformTestCase):
    def test_output(self):
        tests = {
            ("iam", "default"): expected_iam_default_output,
            ("iam", "prod"): expected_iam_prod_output,
            ("vpc", "default"): expected_vpc_default_output,
            ("vpc", "prod"): expected_vpc_prod_output,
        }
        for ((stack, workspace), expected) in sorted(tests.items()):
            with self.subTest(f"{stack}/{workspace}"):

                # Change to the Terraform project directory,
                # relative to this test file rather than where
                # the unittest command is running from.
                self.chdir(f"../stacks/{stack}")

                try:

                    # Run terraform init to set up the backend and plugins etc.
                    self.terraform_init()

                    # Select the workspace for this test.
                    self.terraform("workspace", "select", workspace)

                    # Run terraform apply to create resources.
                    self.terraform_apply()

                    # Run terraform output and check the results.
                    output = self.terraform_output_json()
                    self.assertEqual(expected, output)

                finally:

                    # Run terraform destroy to clean up resources.
                    self.terraform_destroy()
