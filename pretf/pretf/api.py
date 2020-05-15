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
    If the path is not anchored (i.e. does not start with ./ or ../ or /)
    then it will check the current directory and all parent directories
    until found.

    """

    from pretf.test import PretfProxy

    if isinstance(cwd, Path):
        # Use path as-is.
        path = cwd
    elif isinstance(cwd, str):
        if cwd.startswith("./") or cwd.startswith("../") or cwd.startswith("/"):
            # Use path as-is.
            path = Path(cwd)
        else:
            # Look for this unanchored path in the current directory
            # and all parent directories until found.
            here = Path.cwd()
            while True:
                path = here / cwd
                if path.is_dir():
                    # Use this matching directory.
                    break
                elif here.parent == here:
                    # Reached the top, use the path as a relative path
                    # and let Terraform give an error.
                    path = Path(cwd)
                    break
                else:
                    # Move up a directory and let it try there.
                    here = here.parent
    else:
        raise TypeError(cwd)

    if is_verbose(verbose) or not path.is_dir():

        # Find the calling directory of this function, usually the directory
        # containing the pretf.workflow.py file that has called this function.
        frame = inspect.currentframe()
        if not frame:
            raise Exception("get_outputs() called from unknown frame")
        caller_frame = frame.f_back
        if not caller_frame:
            raise Exception("get_outputs() called from unknown caller")
        caller_info = inspect.getframeinfo(caller_frame)
        caller_file = caller_info.filename

        if path.is_dir():
            log.ok(f"outputs: {cwd} -> {caller_file}")
        else:
            if path.exists():
                raise log.bad(
                    f"get_outputs({cwd!r}) in {caller_file}: {path} is not a directory"
                )
            else:
                raise log.bad(
                    f"get_outputs({cwd!r}) in {caller_file}: {path} does not exist"
                )

    outputs = PretfProxy(cwd=path, verbose=False).output()

    values = {}
    for name, data in outputs.items():
        values[name] = data["value"]

    return values


__all__ = ["block", "get_outputs", "labels", "log"]
