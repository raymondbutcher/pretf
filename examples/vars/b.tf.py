from pretf.api import block


def pretf_blocks(var):
    yield block("output", "two_attr", {"value": var.two})

    yield block("output", "two_dict", {"value": var["two"]})

    yield block("variable", "three", {"default": 3})

    yield block("output", "three", {"value": var.three})

    yield block("variable", "four", {})

    yield block("output", "four", {"value": var.four})
