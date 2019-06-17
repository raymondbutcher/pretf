from pretf.api import block
from pretf.test import SimpleTest
from pretf.workflow import delete_files


class TestExample(SimpleTest):
    """
    This test class shows how to create Terraform configuration,
    run terraform, and then make assertions about the output.

    Each test_* method runs in the order they are defined here.
    If any of them fail then testing is stopped automatically.

    """

    def test_create(self):
        """
        Create the Terraform configuration.

        """

        delete_files("*.json")

        with self.create("one.tf.json"):
            test = yield block("variable", "test", {"default": True})
            yield block("output", "test", {"value": test})

    def test_init(self):
        """
        Run 'terraform init'.

        """

        self.init()

    def test_apply(self):
        """
        Run 'terraform apply'.

        """

        self.apply()

    def test_output(self):
        """
        Run 'terraform output' and check that it is as expected.

        """

        output = self.output(json=True)
        assert output == {"test": {"sensitive": False, "type": "bool", "value": True}}

    def test_destroy(self):
        """
        Run 'terraform destroy'.

        """

        self.destroy()
