import collections
import contextlib
import functools
import inspect
import os
import sys
import warnings
from json import dump as json_dump
from json import loads as json_loads
from subprocess import CompletedProcess
from typing import Any, Callable, Dict, Generator, List, Union

import pytest

from pretf import render, workflow


class SimpleTestMeta(type):
    def __new__(cls, name, bases, dct):  # type: ignore

        for name, value in list(dct.items()):
            if name.startswith("test_") and callable(value):
                dct[name] = pretf_test_function(value)

        return super().__new__(cls, name, bases, dct)


def pretf_test_function(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped(self: Any, *args: tuple, **kwargs: dict) -> Any:

        if hasattr(self.__class__, "_failed"):
            pytest.xfail(f"{self.__class__} failed")

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

    return wrapped


class SimpleTest(metaclass=SimpleTestMeta):
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

    # Terraform command.

    def terraform(self, *args: str) -> CompletedProcess:

        # Ignore "Boto3 ResourceWarning: unclosed <ssl.SSLSocket ...>"
        # because it is just HTTP connections that get reused or closed
        # as necessary.
        warnings.simplefilter("ignore", ResourceWarning)

        # Make Terraform output more suitable for tests.
        os.environ["TF_IN_AUTOMATION"] = "1"
        os.environ["PRETF_CAPTURE_OUTPUT"] = "1"

        argv = sys.argv
        sys.argv = ["terraform", *args]

        try:
            proc = workflow.execute_terraform()
        finally:
            sys.argv = argv

        return proc

    # Terraform shortcuts.

    def apply(self) -> dict:
        """
        Runs terraform apply, parses the text output for output values,
        and returns them as a dictionary. The outputs will all be strings,
        use the output() function if correct output types are required.

        """

        proc = self.terraform(
            "apply", "-input=false", "-auto-approve=true", "-no-color"
        )
        outputs = {}
        for line in proc.stdout.split("Outputs:\n", 1)[1].splitlines():
            line = line.strip()
            if line:
                name, value = line.split("=", 1)
                outputs[name.strip()] = value.strip()
        return outputs

    def destroy(self) -> None:
        self.terraform("destroy", "-input=false", "-auto-approve=true")

    def init(self) -> None:
        self.terraform("init", "-input=false")

    def output(self, json: bool = True) -> Union[CompletedProcess, dict]:
        if json:
            proc = self.terraform("output", "-json")
            return json_loads(proc.stdout)
        else:
            proc = self.terraform("output")
            return proc.stdout
