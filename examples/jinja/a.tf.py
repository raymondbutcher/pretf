from pretf.api import block


def pretf_blocks(var):
    yield block("resource", "random_id", "from_python", {
        "byte_length": var.byte_length,
        "prefix": "python-",
    })
