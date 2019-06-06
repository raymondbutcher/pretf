import json
import re
from pathlib import Path

import hcl

from . import log


def parse_tf_file(path: Path) -> list:
    """
    This is a really bad parser for *.tf and *.tfvars files,
    with the only goal being to parse variable definitions and
    variable values.

    From https://www.hashicorp.com/blog/terraform-0-12-reliable-json-syntax

        In future versions of Terraform, we will also support native tooling
        to convert HCL to JSON and JSON to HCL cleanly (including comments).

    When that happens, consider replacing this code with calls to that.

    """

    with path.open() as open_file:
        contents = open_file.read()

    # Add quotes around bare expressions
    # because the parser doesn't support them.
    fixed = re.sub(
        r'^(\s*[a-z_-]+\s*=\s*)([^{\s"][^"\r\n]+)$',
        r'\1"\2"',
        contents,
        flags=re.MULTILINE,
    )

    # Parse the HCL.
    # Ignore parsing errors if the file is empty or only contains comments.
    try:
        parsed = hcl.loads(fixed)
    except ValueError:
        parsed = {}
        in_comment = False
        for line in fixed:
            line = line.lstrip()
            if not line:
                continue
            if line.startswith("/*"):
                in_comment = True
            elif in_comment:
                if line.startswith("*/"):
                    in_comment = False
            elif line.startswith("#"):
                continue
            else:
                log.bad(f"error parsing {path}")
                raise

    return parsed


def get_variables_from_block(block):
    if "variable" in block:
        variable = block["variable"]
        if isinstance(variable, dict):
            variables = [variable]
        else:
            variables = variable
        for variable in variables:
            for name, block in variable.items():
                if "default" in block:
                    yield {"name": name, "default": block["default"]}
                else:
                    yield {"name": name}


def get_variables_from_file(path):
    if path.name.endswith(".tf"):
        contents = parse_tf_file(path)
        if isinstance(contents, dict):
            blocks = [contents]
        else:
            blocks = contents
        for block in blocks:
            yield from get_variables_from_block(block)
    elif path.name.endswith(".tfvars"):
        contents = parse_tf_file(path)
        for name, value in contents.items():
            yield {"name": name, "value": value}
    elif path.name.endswith(".tf.json"):
        yield from get_variables_from_tf_json(path)
    elif path.name.endswith(".tfvars.json"):
        yield from get_variables_from_tfvars_json(path)


def get_variables_from_tf_json(path):

    with open(path) as open_file:
        contents = json.load(open_file)

    if isinstance(contents, dict):
        blocks = [contents]
    else:
        blocks = contents

    for block in blocks:
        yield from get_variables_from_block(block)


def get_variables_from_tfvars_json(path):

    with open(path) as open_file:
        contents = json.load(open_file)

    if isinstance(contents, dict):
        blocks = [contents]
    else:
        blocks = contents

    for block in blocks:
        for name, value in block.items():
            yield {"name": name, "value": value}
