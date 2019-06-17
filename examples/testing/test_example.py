from pretf.api import block
from pretf.test import SimpleTest
from pretf.workflow import delete_files


class TestExample(SimpleTest):
    """
    This test class shows how to create Terraform configuration,
    run Terraform, and then make assertions about its output.

    Each test_* method runs in the order they are defined here.
    If any of them fail then testing is stopped automatically.

    """

    def test_create(self):

        delete_files("*.json")

        with self.create("one.tf.json"):
            one = yield block("variable", "one", {"default": True})
            yield block("output", "one", {"value": one})

        self.init()
        self.apply()

        output = self.output(json=True)

        assert output == {"one": {"sensitive": False, "type": "bool", "value": True}}

    def test_change(self):

        with self.create("one.tf.json"):
            one = yield block("variable", "one", {"default": False})
            yield block("output", "one", {"value": one})

        with self.create("two.tf.json"):
            two = yield block("variable", "two", {"default": True})
            yield block("output", "two", {"value": two})

        self.apply()

        output = self.output(json=True)

        assert output == {
            "one": {"sensitive": False, "type": "bool", "value": False},
            "two": {"sensitive": False, "type": "bool", "value": True},
        }

    def test_destroy(self):
        self.destroy()
