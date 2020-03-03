from pretf import test, workflow
from pretf.blocks import output, variable


class TestExample(test.SimpleTest):
    """
    Each test_* method runs in the order they are defined here.
    If any of them fail then subsequent tests do not run.

    """

    def test_create(self):

        workflow.delete_files("*.json")

        with self.create("one.tf.json"):
            one = yield variable.one(default=True)
            yield output.one(value=one)

        self.tf.init()

        outputs = self.tf.apply()
        assert outputs == {"one": True}

    def test_change(self):

        with self.create("one.tf.json"):
            one = yield variable.one(default=False)
            yield output.one(value=one)

        with self.create("two.tf.json"):
            two = yield variable.two(default={"x": [1, 2, 3], "y": 4})
            yield output.two(value=two)

        outputs = self.tf.apply()
        assert outputs == {"one": False, "two": {"x": [1, 2, 3], "y": 4}}

    @test.always
    def test_destroy(self):
        self.tf.destroy()
