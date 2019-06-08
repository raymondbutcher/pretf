import unittest

from pretf.api import tf
from pretf.collections import collect
from pretf.render import Block, VariableNotPopulated


@collect
def iam_user(var):

    # Yield variable to define function inputs.
    yield tf("variable.name")
    yield tf("variable.path", {"default": "/"})

    # Yield regular resources to include in JSON.
    user = yield tf(
        f"resource.aws_iam_user.{var.name}", {"name": var.name, "path": var.path}
    )

    # Yield outputs to define attributes.
    yield tf("output.arn", {"value": user.arn})
    yield tf("output.user", {"value": user})
    yield tf("output.dict", {"value": {"anything": True}})


@collect
def iam_users(var):

    yield tf("variable.names")

    for name in var.names:
        yield iam_user(name=name)


class TestCollections(unittest.TestCase):
    def test_collect(self):

        # Create collection with bad inputs.
        with self.assertRaises(VariableNotPopulated):
            iam_user()

        # Call collection with valid inputs.
        peanut = iam_user(name="peanut")

        # The collection is iterable and contains yielded blocks,
        # excluding variables and outputs.
        blocks = list(peanut)
        expected = [
            {"resource": {"aws_iam_user": {"peanut": {"name": "peanut", "path": "/"}}}}
        ]
        self.assertEqual(expected, blocks)

        # Yielded outputs can be accessed as attributes.
        # This one is a string (attribute of a Block).
        arn = peanut.arn
        expected = "${aws_iam_user.peanut.arn}"
        self.assertEqual(expected, arn)

        # This one is a Block.
        user = peanut.user
        self.assertTrue(isinstance(user, Block))
        expected = "${aws_iam_user.peanut.name}"
        self.assertEqual(expected, user.name)

        # This one is a dict.
        self.assertEqual(peanut.dict, {"anything": True})

        # This one doesn't exist
        with self.assertRaises(AttributeError):
            peanut.nope
