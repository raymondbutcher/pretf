import collections
import contextlib
import functools
import inspect
import os
from json import dump as json_dump
from json import loads as json_loads
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Callable, Dict, Generator, List, Optional, Union

import pytest

from pretf import parser, render, util, workflow


class TerraformProxy:
    def __init__(self, cwd: Union[Path, str] = "", verbose: Optional[bool] = False):
        if not isinstance(cwd, Path):
            cwd = Path(cwd)
        self.cwd = cwd
        self.env = os.environ.copy()
        self.env["TF_IN_AUTOMATION"] = "1"
        self.env["PRETF_VERBOSE"] = "1" if verbose else "0"
        self.verbose = verbose

    # Calling the object just returns another object with the specified path.

    def __call__(self, cwd: Union[Path, str] = "") -> "TerraformProxy":
        return self.__class__(cwd or self.cwd)

    # Context manager.
    # It doesn't do anything but can make the test code easier to follow.

    def __enter__(self) -> "TerraformProxy":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        return None

    # Terraform command.

    def execute(self, *args: str) -> CompletedProcess:
        return workflow.execute_terraform(
            args=args, cwd=self.cwd, env=self.env, capture=True, verbose=self.verbose
        )

    # Terraform shortcuts.

    def apply(self, *args: str) -> dict:
        """
        Runs terraform apply, parses the output for output values,
        and returns them as a dictionary.

        """

        apply_args = ["apply", "-input=false", "-auto-approve=true", "-no-color"]
        for arg in args:
            if arg not in apply_args:
                apply_args.append(arg)
        return parser.parse_apply_outputs(self.execute(*apply_args).stdout)

    def destroy(self, *args: str) -> str:
        """
        Runs terraform destroy and returns the stdout.

        """

        destroy_args = ["destroy", "-input=false", "-auto-approve=true"]
        for arg in args:
            if arg not in destroy_args:
                destroy_args.append(arg)
        return self.execute(*destroy_args).stdout

    def get(self, *args: str) -> str:
        """
        Runs terraform get and returns the stdout.

        """

        get_args = ["get"]
        for arg in args:
            if arg not in get_args:
                get_args.append(arg)
        return self.execute(*get_args).stdout

    def init(self, *args: str) -> str:
        """
        Runs terraform init and returns the stdout.

        """

        init_args = ["init", "-input=false"]
        for arg in args:
            if arg not in init_args:
                init_args.append(arg)
        return self.execute(*init_args).stdout

    def output(self, *args: str) -> dict:
        """
        Runs terraform output and returns the JSON.

        """

        output_args = ["output", "-json"]
        for arg in args:
            if arg not in output_args:
                output_args.append(arg)
        return json_loads(self.execute(*output_args).stdout)

    def plan(self, *args: str) -> str:
        """
        Runs terraform plan and returns the stdout.

        """

        plan_args = ["plan", "-input=false"]
        for arg in args:
            if arg not in plan_args:
                plan_args.append(arg)
        return self.execute(*plan_args).stdout


class PretfProxy(TerraformProxy):
    def execute(self, *args: str) -> CompletedProcess:
        return util.execute(
            file="pretf",
            args=["pretf"] + list(args),
            cwd=self.cwd,
            env=self.env,
            capture=True,
            verbose=self.verbose,
        )


class SimpleTestMeta(type):
    def __new__(cls, name, bases, dct):  # type: ignore
        """
        Wraps all test methods with the pretf_test_function() decorator.

        """

        for name, value in list(dct.items()):
            if name.startswith("test_") and callable(value):
                dct[name] = pretf_test_function(value)

        return super().__new__(cls, name, bases, dct)

    def __init__(self, name, bases, dct):  # type: ignore
        """
        Adds any test method using the @always decorator to cls._always
        so the pretf_test_function() can run it even when previous tests
        have failed.

        """

        super().__init__(name, bases, dct)

        self._always = set()
        for name, value in list(dct.items()):
            if hasattr(value, "_always"):
                self._always.add(value.__name__)


def pretf_test_function(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped(self: Any, *args: tuple, **kwargs: dict) -> Any:

        if hasattr(self.__class__, "_failed"):
            if func.__name__ not in self._always:
                pytest.xfail(f"{self.__class__} failed")

        # Change the working directory to the test file.
        cwd_before = os.getcwd()
        func_file = inspect.getfile(func)
        func_dir = os.path.dirname(func_file)
        os.chdir(func_dir)

        try:

            if inspect.isgeneratorfunction(func):

                gen = func(self, *args, **kwargs)

                yielded = None
                while True:

                    try:
                        yielded = gen.send(yielded)
                    except StopIteration:
                        break

                    if not hasattr(self, "_create") or not self._create:
                        raise Exception(
                            "yield must be called inside a self.create() context"
                        )

                    file_name = self._create[-1]
                    for block in render.unwrap_yielded(yielded):
                        self._blocks[file_name].append(block)

            else:
                return func(self, *args, **kwargs)

        except Exception:

            self.__class__._failed = func.__name__
            raise

        finally:

            os.chdir(cwd_before)

    return wrapped


class SimpleTest(metaclass=SimpleTestMeta):

    pretf = PretfProxy()
    tf = TerraformProxy()

    @contextlib.contextmanager
    def create(self, file_name: str) -> Generator[None, None, None]:

        assert file_name.endswith(".tf.json") or file_name.endswith(".tfvars.json")
        assert "/" not in file_name

        if not hasattr(self, "_blocks"):
            self._blocks: Dict[str, list] = collections.defaultdict(list)

        if not hasattr(self, "_create"):
            self._create: List[str] = []

        self._create.append(file_name)

        yield

        self._create.pop()

        contents = self._blocks.pop(file_name)

        with open(file_name, "w") as open_file:
            json_dump(contents, open_file, indent=2, default=render.json_default)


def always(func: Callable) -> Callable:
    """
    Marks a test method to run even when previous tests have failed.

    """

    func._always = True  # type: ignore
    return func
