from typing import Any

from . import labels, log
from .render import Block


def block(block_type, *args: Any) -> Block:
    if args:
        body = args[-1]
        labels = list(args[:-1])
    else:
        body = None
        labels = []
    return Block(block_type, labels, body)


__all__ = ["block", "labels", "log"]
