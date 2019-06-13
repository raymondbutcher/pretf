from pretf.api import block


def pretf_blocks(var):
    yield block("variable", "one", {"default": 1})

    yield block("output", "one", {"value": var.one})

    yield block("variable", "two", {"default": 2})
