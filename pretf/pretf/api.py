import inspect
from pathlib import Path
from typing import Any, Optional, Union

from . import labels, log
from .blocks import Block
from .util import is_verbose


def block(block_type: str, *args: Any) -> Block:
    if args:
        body = args[-1]
        labels = list(args[:-1])
    else:
        body = None
        labels = []
    return Block(block_type, labels, body)


def get_outputs(cwd: Union[Path, str], verbose: Optional[bool] = None) -> dict:
    """
    Runs `pretf output` in the specified directory and returns the values.

    """

    from pretf.test import PretfProxy

    if is_verbose(verbose):

        # Find directory of caller file.
        caller_frame = inspect.currentframe().f_back  # type: ignore
        caller_info = inspect.getframeinfo(caller_frame)
        caller_file = caller_info.filename

        log.ok(f"outputs: {cwd} -> {caller_file}")

    outputs = PretfProxy(cwd=cwd, verbose=False).output()

    values = {}
    for name, data in outputs.items():
        values[name] = data["value"]

    return values


__all__ = ["block", "get_outputs", "labels", "log"]
