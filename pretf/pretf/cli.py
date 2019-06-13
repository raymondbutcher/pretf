import os
import sys

from . import log, workflow
from .exceptions import FunctionNotFoundError, VariableError
from .version import __version__


def main() -> None:
    """
    This is the pretf CLI tool entrypoint.

    """

    # Version command.
    args = sys.argv[1:]
    cmd = args[0] if args else None
    if cmd in ("version", "-v", "-version", "--version"):
        print(f"Pretf v{__version__}")
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
