from pretf.blocks import data, locals, module, output, provider, resource, variable
from pretf.render import unwrap_yielded


def test_data():
    assert str(data) == "<module 'pretf.blocks.data'>"
    assert str(data.null_data_source) == "<module 'pretf.blocks.data.null_data_source'>"
    assert str(data.null_data_source.test) == "${data.null_data_source.test}"

    # Use index access for dynamic names.
    assert str(data.null_data_source["test"]) == "${data.null_data_source.test}"


def test_locals():
    assert str(locals) == "<module 'pretf.blocks.locals'>"
    assert str(locals.test) == "${local.test}"

    # Confirm that the locals block works to generate configuration.
    assert list(unwrap_yielded(locals(a=1, b=2, c=3))) == [
        {"locals": {"a": 1, "b": 2, "c": 3}}
    ]


def test_module():
    assert str(module) == "<module 'pretf.blocks.module'>"
    assert str(module.test) == "${module.test}"

    # Pass in a dictionary for the body.
    one = module.one({"a": 1, "b": 2, "c": 3})
    assert str(one) == "${module.one}"

    # Pass in multiple dictionaries for the body.
    two = module.two({"a": 1, "b": 2}, {"c": 3})
    assert str(two) == "${module.two}"

    # Pass in keyword arguments for the body.
    three = module.three(a=1, b=2, c=3)
    assert str(three) == "${module.three}"

    # Pass in a dictionary and keyword arguments for the body.
    four = module.four({"a": 1}, b=2, c=3)
    assert str(four) == "${module.four}"

    # Pass in multiple dictionaries and keyword arguments for the body.
    five = module.five({"a": 1}, {"b": 2}, c=3)
    assert str(five) == "${module.five}"


def test_output():
    assert str(output) == "<module 'pretf.blocks.output'>"
    assert str(output.test) == "${output.test}"


def test_provider():
    assert str(provider) == "<module 'pretf.blocks.provider'>"
    assert str(provider.aws) == "aws"


def test_resource():
    assert str(resource) == "<module 'pretf.blocks.resource'>"
    assert (
        str(resource.null_resource) == "<module 'pretf.blocks.resource.null_resource'>"
    )
    assert str(resource.null_resource.test) == "${null_resource.test}"


def test_variable():
    assert str(variable) == "<module 'pretf.blocks.variable'>"
    assert str(variable.test) == "${var.test}"
