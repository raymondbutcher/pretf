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
