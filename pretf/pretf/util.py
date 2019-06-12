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
from pathlib import Path, PurePath
from threading import Lock
from types import ModuleType
from typing import Generator, Optional, Sequence, Union

from . import log


def execute(
    file: str, args: Sequence[str], env: Optional[dict] = None, verbose: bool = True
) -> int:
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
                exit_code = exit_status >> 8
                return exit_code
    return 1


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


def once(func):

    locks = defaultdict(Lock)

    @lru_cache(maxsize=None)
    def get_key(*args, **kwargs):
        return object()

    @wraps(func)
    def wrapped(*args, **kwargs):
        key = get_key(*args, **kwargs)
        if locks[key].acquire(blocking=False):
            return func(*args, **kwargs)

    return wrapped
