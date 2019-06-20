"""
This file demonstrates that tests can use *.tf.py files to
create *.tf.json files. There is nothing actually dynamic
in this example, and it would normally be better off as
a standard *.tf file. It is just done this way to test
that it works.

"""

from pretf.api import block


def pretf_blocks(var):
    additional = yield block(
        "resource",
        "random_id",
        "additional",
        {"byte_length": 2, "prefix": var.additional_prefix},
    )
    yield block("output", "additional", {"value": additional.hex})
