from pathlib import Path

from pretf.tests import TerraformTestCase


class TestAWS(TerraformTestCase):

    cwd = Path(__file__).parent.parent
    # init = True
    # apply = True

    def test_output(self):
        output = self.terraform_output_json()
        expected = {
            "total_bytes": {"sensitive": False, "type": "number", "value": 63},
            "total_files": {"sensitive": False, "type": "number", "value": 5},
        }
        self.assertEqual(expected, output)
