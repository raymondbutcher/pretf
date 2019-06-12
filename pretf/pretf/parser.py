import enum
import json
import re
from pathlib import Path
from typing import Generator, List

import hcl

from . import log


class State(enum.Enum):
    BLOCK = enum.auto()
    ESCAPE = enum.auto()
    ROOT = enum.auto()
    STRING = enum.auto()


def clean_block_string(block_string: str) -> str:

    # Remove comments.
    lines = []
    in_comment = False
    for line in block_string.splitlines():
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
    block_string = "\n".join(lines)

    # Add quotes around bare expressions
    # because the parser doesn't support them.
    block_string = re.sub(
        r'^(\s*[a-z_-]+\s*=\s*)([^[{\s"][^"\r\n]+)$',
        r'\1"\2"',
        block_string,
        flags=re.MULTILINE,
    )

    return block_string


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


def parse_tf_file_for_block_strings(path: Path) -> Generator[str, None, None]:

    states = [State.ROOT]

    buffer = []

    for char in read_chars_from_file(path):

        buffer.append(char)

        state = states[-1]

        if state is State.ROOT:

            if char == '"':
                states.append(State.STRING)
            elif char == "{":
                if buffer[-1:] != "\n":
                    buffer.append("\n")
                states.append(State.BLOCK)
            elif char == "\n":
                block = clean_block_string("".join(buffer))
                if block:
                    yield block
                buffer.clear()

        elif state is State.STRING:

            if char == "\\":
                states.append(State.ESCAPE)
            elif char == '"':
                states.pop()

        elif state is State.BLOCK:

            if char == '"':
                states.append(State.STRING)
            elif char == "{":
                states.append(State.BLOCK)
            elif char == "}":
                if buffer[-1:] != "\n":
                    buffer[-1] = "\n"
                    buffer.append(char)
                states.pop()
                if states[-1] is State.ROOT:
                    block = clean_block_string("".join(buffer))
                    if block:
                        yield block
                    buffer.clear()

        else:
            raise ValueError(state)

    # There shouldn't be anything left over.
    block = clean_block_string("".join(buffer))
    if block:
        raise ValueError(block)


def parse_tf_file_for_variables(path: Path) -> List[dict]:
    """
    This is a really bad parser for *.tf and *.tfvars files,
    with the only goal being to parse variable definitions and
    variable values.

    From https://www.hashicorp.com/blog/terraform-0-12-reliable-json-syntax

        In future versions of Terraform, we will also support native tooling
        to convert HCL to JSON and JSON to HCL cleanly (including comments).

    When that happens, consider replacing this code with calls to that.

    """

    blocks = []

    for block_string in parse_tf_file_for_block_strings(path):
        if block_string.strip().startswith("variable "):
            try:
                parsed = hcl.loads(block_string)
            except ValueError:
                log.bad(f"error parsing {path}")
                print(block_string)
                raise
            else:
                blocks.append(parsed)

    return blocks


def parse_json_file_for_blocks(path: Path) -> List[dict]:

    with open(path) as open_file:
        contents = json.load(open_file)

    if isinstance(contents, dict):
        blocks = [contents]
    else:
        blocks = contents

    return blocks


def parse_tfvars_file_for_variables(path: Path) -> List[dict]:
    cleaned = clean_block_string(path.read_text())
    if cleaned:
        return [hcl.loads(cleaned)]
    else:
        return []


def read_chars_from_file(path: Path) -> Generator[str, None, None]:
    with path.open() as open_file:
        while True:
            char = open_file.read(1)
            if char:
                yield char
            else:
                break
