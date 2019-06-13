import os
import sys
from typing import List, Optional, Tuple

from . import log, workflow
from .exceptions import FunctionNotFoundError, VariableError
from .version import __version__


def main() -> None:
    """
    This is the pretf CLI tool entrypoint.

    """

    cmd, args, flags = parse_args()

    if cmd == "version":
        print(f"Pretf v{__version__}")

    if cmd in (None, "fmt", "help", "version"):
        skip = True
    elif cmd == "workspace" and args and args[0] == "show":
        skip = True
    else:
        skip = False

    if skip:
        exit_code = workflow.execute_terraform(verbose=False)
        sys.exit(exit_code)

    try:

        if os.path.exists("pretf.py"):
            exit_code = workflow.custom("pretf.py")
        else:
            exit_code = workflow.default()

    except FunctionNotFoundError as error:

        log.bad(error)
        exit_code = 1

    except VariableError as error:

        if hasattr(error, "errors"):
            for error in error.errors:
                log.bad(error)
        else:
            log.bad(error)
        exit_code = 1

    sys.exit(exit_code)


def parse_args() -> Tuple[Optional[str], List[str], List[str]]:

    cmd = None
    args = []
    flags = []

    help_flags = set(("-h", "-help", "--help"))
    version_flags = set(("-v", "-version", "--version"))

    for arg in sys.argv[1:]:
        if arg.startswith("-"):
            if not cmd and arg in help_flags:
                cmd = "help"
            elif not cmd and arg in version_flags:
                cmd = "version"
            else:
                flags.append(arg)
        elif not cmd:
            cmd = arg
        else:
            args.append(arg)

    return (cmd, args, flags)
