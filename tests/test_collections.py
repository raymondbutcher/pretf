import pytest

from pretf.api import block
from pretf.collections import collect
from pretf.exceptions import VariableNotPopulatedError
from pretf.render import Block


@collect
def iam_user(var):
    # Inputs.
    yield block("variable", "name", {})
    yield block("variable", "path", {"default": "/"})

    # Resources.
    user = yield block(
        "resource", "aws_iam_user", var.name, {"name": var.name, "path": var.path}
    )

    # Outputs.
    yield block("output", "name", {"value": var.name})
    yield block("output", "resource", {"value": user})


@collect
def iam_group(var):
    # Inputs.
    yield block("variable", "name", {})
    yield block("variable", "path", {"default": "/"})

    # Resources.
    group = yield block("resource", "aws_iam_group", var.name, {"name": var.name})

    # Outputs.
    yield block("output", "name", {"value": var.name})
    yield block("output", "resource", {"value": group})


@collect
def iam_group_with_users(var):
    # Inputs.
    yield block("variable", "group_name", {})
    yield block("variable", "user_names", {})

    # Yield resources from a nested collection.
    group = yield iam_group(name=var.group_name)

    # Yield resources from a nested collection.
    users = {}
    for name in var.user_names:
        user = yield iam_user(name=name)
        users[name] = user.resource

    # Yield resources from a nested collection,
    # using "yield from" this time.
    # It can be assigned to a variable this way.
    yield from aws_iam_user_group_membership(group=group.resource, users=users)

    # Outputs.
    yield block("output", "group", {"value": group.resource})
    yield block("output", "users", {"value": group.resource})


@collect
def aws_iam_user_group_membership(var):
    # Inputs.
    yield block("variable", "group", {})
    yield block("variable", "users", {})

    # Resources.
    group_label = str(var.group).split(".")[-1]
    for user_label, user in sorted(var.users.items()):
        label = f"{user_label}_in_{group_label}"
        yield block(
            "resource",
            "aws_iam_user_group_membership",
            label,
            {"user": user.name, "groups": [var.group.name]},
        )


def test_collect():

    # Create collection with bad inputs.
    with pytest.raises(VariableNotPopulatedError):
        iam_user()

    # Call collection with valid inputs.
    peanut = iam_user(name="peanut")

    # The collection is iterable and contains yielded blocks,
    # excluding variables and outputs.
    expected = [
        {"resource": {"aws_iam_user": {"peanut": {"name": "peanut", "path": "/"}}}}
    ]
    assert list(peanut) == expected

    # Yielded outputs can be accessed as attributes.
    # This one is a simple string..
    assert peanut.name == "peanut"

    # This one is a Block.
    user = peanut.resource
    assert isinstance(user, Block)
    assert user.arn == "${aws_iam_user.peanut.arn}"

    # This one doesn't exist
    with pytest.raises(AttributeError):
        peanut.nope


def test_nested_collections():

    # Create a collection that has nested collections.
    result = iam_group_with_users(group_name="dogs", user_names=["peanut", "cornelius"])

    # Check it created the resources from the nested collections.
    expected = [
        {"resource": {"aws_iam_group": {"dogs": {"name": "dogs"}}}},
        {"resource": {"aws_iam_user": {"peanut": {"name": "peanut", "path": "/"}}}},
        {
            "resource": {
                "aws_iam_user": {"cornelius": {"name": "cornelius", "path": "/"}}
            }
        },
        {
            "resource": {
                "aws_iam_user_group_membership": {
                    "cornelius_in_dogs": {
                        "groups": ["${aws_iam_group.dogs.name}"],
                        "user": "${aws_iam_user.cornelius.name}",
                    }
                }
            }
        },
        {
            "resource": {
                "aws_iam_user_group_membership": {
                    "peanut_in_dogs": {
                        "groups": ["${aws_iam_group.dogs.name}"],
                        "user": "${aws_iam_user.peanut.name}",
                    }
                }
            }
        },
    ]
    assert list(result) == expected
