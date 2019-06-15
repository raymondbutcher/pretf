from pathlib import Path

from pretf.tests import TerraformTestCase


class TestVars(TerraformTestCase):

    cwd = Path(__file__).parent.parent
    init = True
    apply = True

    def test_output(self):
        output = self.terraform_output_json()
        expected = {
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

        self.assertEqual(expected, output)
