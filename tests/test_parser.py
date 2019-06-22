from pretf import parser

apply_stdout_strings = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

one = one
two =
three = three
"""

apply_stdout_numbers = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

one = 1
two = 22
three = 3.3
four = 4 string
"""

apply_stdout_bools = """
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

one = true
two = false
three = true string
four = false string
"""


def test_apply_outputs_parser():

    outputs = parser.parse_apply_outputs(apply_stdout_strings)

    assert outputs == {"one": "one", "two": "", "three": "three"}

    outputs = parser.parse_apply_outputs(apply_stdout_numbers)

    assert outputs == {"one": 1, "two": 22, "three": 3.3, "four": "4 string"}

    outputs = parser.parse_apply_outputs(apply_stdout_bools)

    assert outputs == {
        "one": True,
        "two": False,
        "three": "true string",
        "four": "false string",
    }
