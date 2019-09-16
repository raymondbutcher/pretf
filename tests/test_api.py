from pretf.api import block


def test_provider_alias():
    default = block("provider", "aws", {"alias": "nonprod"})
    assert str(default.alias) == "aws.nonprod"


def test_provider_alias_default():
    default = block("provider", "aws", {})
    assert str(default.alias) == "aws.default"


def test_variable():
    one = block("variable", "one", {})
    assert str(one) == "${var.one}"


def test_resource():
    resource = block("resource", "one", "two", {})
    assert str(resource) == "${one.two}"


def test_index_interpolation():
    instance = block("resource", "aws_instance", "www", {}).ipv6_addresses[0]
    assert str(instance) == "${aws_instance.www.ipv6_addresses[0]}"


def test_nested_index_interpolation():
    interpolated = block("resource", "one", "two", {}).list[0].another_list[1]
    assert str(interpolated) == "${one.two.list[0].another_list[1]}"
