import json
import re
import sys
from pathlib import Path
from typing import Generator, List

import hcl2

from . import log


def clean_apply_outputs(outputs_string: str) -> str:

    # Remove comments.
    lines = []
    in_comment = False
    for line in outputs_string.splitlines():
        stripped = line.lstrip()
        if not stripped:
            continue
        if stripped.startswith("/*"):
            in_comment = True
        elif in_comment:
            if stripped.startswith("*/"):
                in_comment = False
        elif stripped.startswith("#"):
            continue
        else:
            lines.append(line)
    outputs_string = "\n".join(lines)

    # Add quotes around bare expressions
    # because the parser doesn't support them.

    space = r" *"
    identifier = r"[a-zA-Z0-9_-]+"
    not_number = r"(?!\d+$|\d+\.\d+$)"
    not_boolean = r"(?!true$|false$)"
    not_list = r"(?!\[)"
    not_map = r"(?!{)"
    not_string = r'(?!")'
    value = r"(\S.*$|$)"

    outputs_string = re.sub(
        f"^{space}({identifier}){space}={space}{not_number}{not_boolean}{not_list}{not_map}{not_string}({value})$",
        r'\1 = "\2"',
        outputs_string,
        flags=re.MULTILINE,
    )

    return outputs_string


def get_outputs_from_block(block: dict) -> Generator[dict, None, None]:

    if "output" not in block:
        return

    output = block["output"]

    if isinstance(output, dict):
        outputs = [output]
    else:
        outputs = output

    for output in outputs:
        for name, block in output.items():
            yield {"name": name, "value": block["value"]}


def parse_apply_outputs(stdout: str) -> dict:

    try:
        outputs_string = stdout.split("Outputs:\n", 1)[1]
    except IndexError:
        return {}

    cleaned = clean_apply_outputs(outputs_string)
    if not cleaned:
        return {}

    try:
        return hcl2.loads(cleaned)
    except Exception as error:
        print(file=sys.stderr)
        log.bad("Error parsing:")
        print(stdout, file=sys.stderr)
        log.bad(f"Raising: {error.__class__.__name__}")
        raise


def parse_environment_variable_for_variables(name: str, value: str) -> dict:
    contents = f"{name[7:]} = {value}"
    return parse_hcl2(contents)


def parse_hcl2(contents: str) -> dict:
    try:
        return hcl2.loads(contents)
    except Exception as error:
        print(file=sys.stderr)
        log.bad("Error parsing:")
        print(contents, file=sys.stderr)
        log.bad(f"Raising: {error.__class__.__name__}")
        raise


def parse_json_file_for_blocks(path: Path) -> List[dict]:

    with open(path) as open_file:
        contents = json.load(open_file)

    if isinstance(contents, dict):
        blocks = [contents]
    else:
        blocks = contents

    return blocks
