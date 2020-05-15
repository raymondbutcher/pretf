import os
import shlex
import sys
from contextlib import contextmanager
from fnmatch import fnmatch
from importlib.abc import Loader
from importlib.util import module_from_spec, spec_from_file_location
from io import StringIO
from pathlib import Path, PurePath
from subprocess import PIPE, CalledProcessError, CompletedProcess, Popen
from threading import Thread
from types import ModuleType
from typing import (
    IO,
    BinaryIO,
    Generator,
    List,
    Optional,
    Sequence,
    TextIO,
    Tuple,
    Union,
)

from . import log


def execute(
    file: str,
    args: Sequence[str],
    cwd: Optional[Union[Path, str]] = None,
    env: Optional[dict] = None,
    capture: bool = False,
    verbose: Optional[bool] = None,
) -> CompletedProcess:
    """
    Executes a command and waits for it to finish.

    If args are provided, then they will be used.

    If args are not provided, and arguments were used to run this program,
    then those arguments will be used.

    If args are not provided, and no arguments were used to run this program,
    and default args are provided, then they will be used.

    Returns the exit code from the command that is run.

    """

    if env is None:
        env = os.environ.copy()

    if is_verbose(verbose):
        log.ok(f"run: {' '.join(shlex.quote(arg) for arg in args)}")

    if capture:
        return _execute_and_capture(file, args, cwd, env, verbose)
    else:
        return _execute(file, args, cwd, env)


def _execute(
    file: str, args: Sequence[str], cwd: Optional[Union[Path, str]], env: dict
) -> CompletedProcess:

    proc = Popen(args, executable=file, cwd=cwd, env=env)

    while True:
        try:
            returncode = proc.wait()
        except KeyboardInterrupt:
            pass
        else:
            break

    if returncode != 0:
        raise CalledProcessError(
            returncode=returncode, cmd=" ".join(shlex.quote(arg) for arg in args),
        )

    return CompletedProcess(args=args, returncode=returncode)


def _execute_and_capture(
    file: str,
    args: Sequence[str],
    cwd: Optional[Union[Path, str]],
    env: dict,
    verbose: Optional[bool],
) -> CompletedProcess:

    stdout_buffer = StringIO()
    stderr_buffer = StringIO()

    proc = Popen(args, executable=file, stdout=PIPE, stderr=PIPE, cwd=cwd, env=env)

    stdout_args: List[Optional[IO]] = [proc.stdout, stdout_buffer]
    if is_verbose(verbose):
        stdout_args.append(sys.stdout)
    stdout_thread = Thread(target=_fan_out, args=stdout_args)
    stdout_thread.start()

    stderr_args = [proc.stderr, stderr_buffer, sys.stderr]
    stderr_thread = Thread(target=_fan_out, args=stderr_args)
    stderr_thread.start()

    while True:
        try:
            returncode = proc.wait()
        except KeyboardInterrupt:
            pass
        else:
            break

    stdout_thread.join()
    stderr_thread.join()

    stdout_buffer.seek(0)
    stderr_buffer.seek(0)

    if returncode != 0:
        raise CalledProcessError(
            returncode=returncode,
            cmd=" ".join(shlex.quote(arg) for arg in args),
            output=stdout_buffer.read(),
            stderr=stderr_buffer.read(),
        )

    return CompletedProcess(
        args=args,
        returncode=returncode,
        stdout=stdout_buffer.read(),
        stderr=stderr_buffer.read(),
    )


def _fan_out(input_steam: BinaryIO, *output_streams: TextIO) -> None:
    while True:
        char = input_steam.read(1).decode()
        if char:
            for output_stream in output_streams:
                output_stream.write(char)
        else:
            break


def find_paths(
    path_patterns: Sequence[str],
    exclude_name_patterns: Sequence[str] = [],
    cwd: Optional[Union[Path, str]] = None,
) -> Generator[Path, None, None]:

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    for pattern in path_patterns:
        for path in cwd.glob(pattern):
            for exclude_name_pattern in exclude_name_patterns:
                if fnmatch(path.name, exclude_name_pattern):
                    break
            else:
                yield path


def find_workflow_path(cwd: Optional[Union[Path, str]] = None) -> Optional[Path]:

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    for name in ("pretf.workflow.py", "pretf.py"):

        path = cwd / name
        if path.exists():
            return path

        for dir_path in path.parents:
            path = dir_path / name
            if path.exists():
                return path

    return None


@contextmanager
def import_file(path: Union[PurePath, str]) -> Generator[ModuleType, None, None]:
    """
    Imports a Python module from any local filesystem path.
    Temporarily alters sys.path to allow the imported module
    to import other modules in the same directory.

    """

    pathdir = os.path.dirname(path)
    if pathdir in sys.path:
        added_to_sys_path = False
    else:
        sys.path.insert(0, pathdir)
        added_to_sys_path = True
    try:
        name = os.path.basename(path).split(".")[0]
        spec = spec_from_file_location(name, str(path))
        module = module_from_spec(spec)
        assert isinstance(spec.loader, Loader)
        loader: Loader = spec.loader
        try:
            loader.exec_module(module)
        except Exception as error:
            log.bad(error)
            raise
        yield module
    finally:
        if added_to_sys_path:
            sys.path.remove(pathdir)


def is_verbose(verbose: Optional[bool], default: bool = True) -> bool:
    if verbose is not None:
        return verbose
    env_verbose = os.environ.get("PRETF_VERBOSE")
    if env_verbose == "1":
        return True
    elif env_verbose == "0":
        return False
    else:
        return default


def parse_args() -> Tuple[Optional[str], List[str], List[str], str]:

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

    config_dir = ""
    if cmd == "apply":
        if args:
            dir_or_plan = args[0]
            if os.path.isdir(dir_or_plan):
                config_dir = dir_or_plan
    elif cmd == "force-unlock":
        if len(args) == 2:
            config_dir = args[1]
    elif cmd in {
        "console",
        "destroy",
        "get",
        "graph",
        "init",
        "plan",
        "refresh",
        "validate",
    }:
        if args:
            config_dir = args[-1]

    return (cmd, args, flags, config_dir)
