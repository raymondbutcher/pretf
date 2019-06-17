import sys
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import List, Optional, Tuple

from . import log, workflow
from .exceptions import FunctionNotFoundError, RequiredFilesNotFoundError, VariableError
from .version import __version__


def main() -> None:
    try:
        proc = run()
    except CalledProcessError as error:
        returncode = error.returncode
    else:
        returncode = proc.returncode
    sys.exit(returncode)


def run() -> CompletedProcess:
    """
    This is the pretf CLI tool entrypoint.

    """

    cmd, args, flags = parse_args()

    if cmd == "version":
        print(f"Pretf v{__version__}")

    if cmd in ("", "fmt", "help", "version"):
        skip = True
    elif cmd == "workspace" and args and args[0] == "show":
        skip = True
    else:
        skip = False

    if skip:
        return workflow.execute_terraform(verbose=False)

    try:

        workflow_path = find_workflow_path()

        if workflow_path:
            return workflow.custom(workflow_path)
        else:
            return workflow.default()

    except FunctionNotFoundError as error:

        log.bad(error)

    except RequiredFilesNotFoundError as error:

        log.bad(f"required: {' '.join(error.name_patterns)}")
        candidates = error.get_candidates()
        if candidates:
            log.bad("found in:")
            for path in candidates:
                log.bad(f"* {path}")

    except VariableError as error:

        if hasattr(error, "errors"):
            for error in error.errors:
                log.bad(error)
        else:
            log.bad(error)

    return CompletedProcess(args=sys.argv, returncode=1)


def find_workflow_path() -> Optional[Path]:

    name = "pretf.py"
    path = Path.cwd() / name
    if path.exists():
        return path

    for dir_path in path.parents:
        path = dir_path / name
        if path.exists():
            return path

    return None


def parse_args() -> Tuple[Optional[str], List[str], List[str]]:

    cmd = ""
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
