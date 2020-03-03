import pytest

from pretf.api import block


@pytest.mark.parametrize(
    "obj,expected",
    [
        (block("provider", "aws", {}), "aws"),
        (block("provider", "aws", {}).alias, "aws"),
        (block("provider", "aws", {"region": "eu-west-1"}), "aws"),
        (block("provider", "aws", {"region": "eu-west-1"}).alias, "aws"),
        (block("provider", "aws", {"alias": "nonprod"}), "aws.nonprod"),
        (block("provider", "aws", {"alias": "nonprod"}).alias, "aws.nonprod"),
        (block("variable", "one", {}), "${var.one}"),
        (block("resource", "one", "two", {}), "${one.two}"),
        (
            block("resource", "aws_instance", "www", {}).ipv6_addresses[0],
            "${aws_instance.www.ipv6_addresses[0]}",
        ),
        (
            block("resource", "one", "two", {}).list[0].another_list[1],
            "${one.two.list[0].another_list[1]}",
        ),
    ],
)
def test_block(obj, expected):
    assert str(obj) == expected
