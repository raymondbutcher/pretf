import sys
from subprocess import CalledProcessError, CompletedProcess
from typing import Union

from . import log, util, workflow
from .exceptions import FunctionNotFoundError, RequiredFilesNotFoundError, VariableError
from .version import __version__


def main() -> None:
    try:
        result = run()
    except CalledProcessError as error:
        sys.exit(error.returncode)
    if isinstance(result, CompletedProcess):
        sys.exit(result.returncode)
    elif isinstance(result, int):
        sys.exit(result)
    raise TypeError(result)


def run() -> Union[CompletedProcess, int]:
    """
    This is the pretf CLI tool entrypoint.

    """

    cmd, args, _, _ = util.parse_args()

    if cmd == "version":
        print(f"Pretf v{__version__}")

    if cmd in {"", "0.12upgrade", "fmt", "help", "version"}:
        skip = True
    elif cmd == "workspace" and args and args[0] == "show":
        skip = True
    else:
        skip = False

    if skip:
        return workflow.execute_terraform(verbose=False)

    try:

        workflow_path = util.find_workflow_path()

        if workflow_path:
            if workflow_path.name == "pretf.py":
                log.bad(
                    "workflow: pretf.py is deprecated, rename it to pretf.workflow.py"
                )
            return workflow.custom(workflow_path)
        else:
            return workflow.default()

    except (log.bad, log.ok):
        pass

    except FunctionNotFoundError as error:

        log.bad(error)

    except RequiredFilesNotFoundError as error:

        log.bad(f"required files not found: {' '.join(error.name_patterns)}")
        candidates = error.get_candidates()
        if candidates:
            log.bad("try changing directory to:")
            for path in candidates:
                log.bad(f"* {path}")

    except VariableError as error:

        if hasattr(error, "errors"):
            for error in error.errors:
                log.bad(error)
        else:
            log.bad(error)

    return CompletedProcess(args=sys.argv, returncode=1)
