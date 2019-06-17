from pretf.api import block
from pretf.test import SimpleTest
from pretf.workflow import delete_files


class TestExample(SimpleTest):
    """
    Each test_* method runs in the order they are defined here.
    If any of them fail then subsequent tests do not run.

    """

    def test_create(self):

        delete_files("*.json")

        with self.create("one.tf.json"):
            one = yield block("variable", "one", {"default": True})
            yield block("output", "one", {"value": one})

        self.init()
        outputs = self.apply()

        assert outputs == {"one": True}

    def test_change(self):

        with self.create("one.tf.json"):
            one = yield block("variable", "one", {"default": False})
            yield block("output", "one", {"value": one})

        with self.create("two.tf.json"):
            two = yield block("variable", "two", {"default": {"x": [1, 2, 3], "y": 4}})
            yield block("output", "two", {"value": two})

        outputs = self.apply()

        assert outputs == {"one": False, "two": {"x": [1, 2, 3], "y": 4}}

    def test_destroy(self):
        self.destroy()
