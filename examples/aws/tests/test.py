from pretf.tests import Any, TerraformTestCase

expected_output = {
    "private_sg_id": {"sensitive": False, "type": "string", "value": Any()},
    "public_sg_id": {"sensitive": False, "type": "string", "value": Any()},
    "total_bytes": {"sensitive": False, "type": "number", "value": 63},
    "total_files": {"sensitive": False, "type": "number", "value": 5},
    "user_pretf_iam_user_1": {
        "sensitive": False,
        "type": "string",
        "value": "pretf-iam-user-1",
    },
    "user_pretf_iam_user_2": {
        "sensitive": False,
        "type": "string",
        "value": "pretf-iam-user-2",
    },
}


class TestAWS(TerraformTestCase):
    def test_output(self):
        # Change to the Terraform project directory,
        # relative to this test file rather than where
        # the unittest command is running from.
        self.chdir("..")

        try:

            # Run terraform init and apply to create resources.
            self.terraform_init()
            self.terraform_apply()

            # Run terraform output and check the results.
            output = self.terraform_output_json()
            self.assertEqual(expected_output, output)

        finally:

            # Run terraform destroy to clean up resources.
            self.terraform_destroy()
