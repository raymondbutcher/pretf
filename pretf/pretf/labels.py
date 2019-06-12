import re

from .render import Block


def clean(label: str) -> str:
    return re.sub(r"__+", "_", re.sub(r"[^a-zA-Z0-9]", "_", label))


def get(block: Block) -> str:
    return block._labels[-1]
