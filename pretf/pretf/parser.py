import json
import sys
from pathlib import Path
from typing import Generator, List

import hcl2

from . import log


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
