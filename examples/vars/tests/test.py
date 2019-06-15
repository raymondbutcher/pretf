from pretf.tests import TerraformTestCase

expected_output = {
    "five": {"sensitive": False, "type": "number", "value": 5},
    "four": {"sensitive": False, "type": "number", "value": 4},
    "one": {"sensitive": False, "type": "number", "value": 1},
    "seven": {
        "sensitive": False,
        "type": ["tuple", ["string", "string"]],
        "value": ["7a", "7b"],
    },
    "six": {
        "sensitive": False,
        "type": ["tuple", ["string", "string"]],
        "value": ["six1", "six2"],
    },
    "three": {"sensitive": False, "type": "number", "value": 3},
    "two_attr": {"sensitive": False, "type": "number", "value": 2},
    "two_dict": {"sensitive": False, "type": "number", "value": 2},
}


class TestVars(TerraformTestCase):
    def test_output(self):

        # Change to the Terraform project directory,
        # relative to this test file rather than where
        # the unittest command is running from.
        self.chdir("..")

        # Run terraform init and apply to create resources.
        self.terraform_init()
        self.terraform_apply()

        # Run terraform output and check the results.
        output = self.terraform_output_json()
        self.assertEqual(expected_output, output)
