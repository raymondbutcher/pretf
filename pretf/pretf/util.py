import errno
import os
import shlex
import sys
from collections import defaultdict
from contextlib import contextmanager
from fnmatch import fnmatch
from functools import lru_cache, wraps
from importlib.abc import Loader
from importlib.util import module_from_spec, spec_from_file_location
from io import StringIO
from pathlib import Path, PurePath
from subprocess import PIPE, CompletedProcess, Popen
from threading import Lock, Thread
from types import ModuleType
from typing import Any, BinaryIO, Callable, Generator, Optional, Sequence, TextIO, Union

from . import log


def execute(
    file: str, args: Sequence[str], env: Optional[dict] = None, verbose: bool = True
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

    if verbose:
        log.ok(f"run: {' '.join(shlex.quote(arg) for arg in args)}")

    if env.get("PRETF_CAPTURE_OUTPUT"):
        return _execute_subprocess(file, args, env)
    else:
        return _execute_fork(file, args, env)


def _execute_fork(file: str, args: Sequence[str], env: dict) -> CompletedProcess:
    returncode = 1
    child_pid = os.fork()
    if child_pid == 0:
        os.execvpe(file, list(args), env)
    else:
        while True:
            try:
                _, exit_status = os.waitpid(child_pid, 0)
            except KeyboardInterrupt:
                pass
            except OSError as error:
                if error.errno == errno.ECHILD:
                    # No child processes.
                    # It has exited already.
                    break
                elif error.errno == errno.EINTR:
                    # Interrupted system call.
                    # This happens when resizing the terminal.
                    pass
                else:
                    # An actual error occurred.
                    raise
            else:
                returncode = exit_status >> 8
                break
    return CompletedProcess(args=args, returncode=returncode)


def _execute_subprocess(file: str, args: Sequence[str], env: dict) -> CompletedProcess:

    stdout_buffer = StringIO()
    stderr_buffer = StringIO()

    proc = Popen(args, executable=file, stdout=PIPE, stderr=PIPE, env=env)

    stdout_thread = Thread(
        target=_fan_out, args=(proc.stdout, sys.stdout, stdout_buffer)
    )
    stdout_thread.start()

    stderr_thread = Thread(
        target=_fan_out, args=(proc.stderr, sys.stderr, stderr_buffer)
    )
    stderr_thread.start()

    returncode = proc.wait()

    stdout_thread.join()
    stderr_thread.join()

    stdout_buffer.seek(0)
    stderr_buffer.seek(0)

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


def once(func: Callable) -> Callable:

    locks: defaultdict = defaultdict(Lock)

    @lru_cache(maxsize=None)
    def get_key(*args: Any, **kwargs: dict) -> object:
        return object()

    @wraps(func)
    def wrapped(*args: Any, **kwargs: dict) -> Any:
        key = get_key(*args, **kwargs)
        if locks[key].acquire(blocking=False):
            return func(*args, **kwargs)

    return wrapped
