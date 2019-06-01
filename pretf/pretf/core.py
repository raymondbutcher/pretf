import errno
import json
import os
import shlex
import sys
from glob import glob
from importlib.machinery import SourceFileLoader
from pathlib import Path

from . import log


class API:
    def __call__(self, path, body=None):
        return Block(path, body or {})

    @staticmethod
    def _get_terraform_blocks(func, kwargs):
        result = func(**kwargs)
        if hasattr(result, "__next__") and hasattr(result, "send"):
            block = next(result)
            yield block
            while True:
                try:
                    block = result.send(block)
                    yield block
                except StopIteration:
                    break
        else:
            yield from result

    @staticmethod
    def _load_functions(paths):
        for path in paths:
            for name in sorted(os.listdir(path)):
                if name.endswith(".tf.py"):
                    base_name = name[:-6]
                    module = SourceFileLoader(base_name, name).load_module()
                    func = module.terraform
                    output_name = base_name + ".tf.json"
                    yield (func, output_name)

    @classmethod
    def _render_function(cls, func, kwargs):
        contents = []
        for block in cls._get_terraform_blocks(func, kwargs):
            if isinstance(block, Block):
                data = dict(iter(block))
            else:
                data = block
            contents.append(data)
        return contents

    @classmethod
    def create(cls, *_paths, **_kwargs):
        """
        Creates *.tf.json files from *.tf.py files in the specified paths.
        Keyword arguments are passed along to the *.tf.py functions.

        """

        result = []
        for func, name in cls._load_functions(_paths or ["."]):

            # Render the Terraform blocks.
            contents = cls._render_function(func, _kwargs)

            # Write JSON file.
            with open(name, "w") as open_file:
                json.dump(contents, open_file, indent=2)

            log.ok(f"create: {name}")
            result.append(name)

        return result

    @staticmethod
    def remove(exclude=None):
        """
        Deletes all *.tf.json files in the current directory.
        Optionally exclude specific files from being deleted.

        """

        old_paths = set(glob("*.tf.json"))

        if isinstance(exclude, str):
            exclude = [exclude]

        if exclude:
            for path in exclude:
                old_paths.discard(path)

        for path in old_paths:
            log.ok(f"remove: {path}")
            os.remove(path)


class Block:
    def __init__(self, path, body):
        self.__path = path
        self.__body = body

    def __iter__(self):
        result = {}
        here = result
        for part in self.__path.split("."):
            here[part] = {}
            here = here[part]
        here.update(self.__body)
        return iter(result.items())

    def __getattr__(self, attr):

        parts = self.__path.split(".")

        if parts[0] == "resource":
            parts.pop(0)
        elif parts[0] == "variable":
            parts[0] = "var"

        parts.append(attr)

        return "${" + ".".join(parts) + "}"

    def __str__(self):
        return self.__path


def execute(file, args=None, default_args=None, env=None, verbose=True):
    """
    Executes a command and waits for it to finish.

    If args are provided, then they will be used.

    If args are not provided, and arguments were used to run this program,
    then those arguments will be used.

    If args are not provided, and no arguments were used to run this program,
    and default args are provided, then they will be used.

    Returns the exit code from the command that is run.

    """

    if args is not None:
        args = [file] + args
    else:
        if sys.argv[1:]:
            args = [file] + sys.argv[1:]
        elif default_args:
            args = [file] + default_args
        else:
            args = [file]

    if verbose:
        log.ok(f"run: {' '.join(shlex.quote(arg) for arg in args)}")

    if env is None:
        env = os.environ

    child_pid = os.fork()
    if child_pid == 0:
        os.execvpe(file, args, env)
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


def mirror(*sources, target=".", exclude=frozenset(["__pycache__"])):
    """
    Creates symlinks from all files and directories in the source
    directories into the target directory. Deletes all existing
    symlinks in the target directory.

    """

    target_path = Path(target)

    # Delete old symlinks in target path.
    for target_file_path in target_path.iterdir():
        if target_file_path.is_symlink():
            target_file_path.unlink()

    # Create new symlinks from source paths.
    for source in sources:
        if target == ".":
            log.ok(f"mirror: {source}")
        else:
            log.ok(f"mirror: {source} to {target}")
        source_path = Path(source)
        for source_file_path in source_path.iterdir():
            if source_file_path.name not in exclude:
                target_file_path = target_path / source_file_path.name
                target_file_path.symlink_to(source_file_path)


tf = API()
