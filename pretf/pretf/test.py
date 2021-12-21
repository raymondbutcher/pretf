import collections
import contextlib
import functools
import inspect
import os
from json import dump as json_dump
from typing import Any, Callable, Dict, Generator, List, Type

import pytest

from pretf import command, render


class SimpleTestMeta(type):
    def __new__(
        cls: Type["SimpleTestMeta"],
        name: str,
        bases: tuple,
        dct: dict,
    ) -> "SimpleTestMeta":
        """
        Wraps all test methods with the pretf_test_function() decorator.

        """

        for name, value in list(dct.items()):
            if name.startswith("test_") and callable(value):
                dct[name] = pretf_test_function(value)

        return super().__new__(cls, name, bases, dct)

    def __init__(self, name: str, bases: tuple, dct: dict) -> None:
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


class SimpleTest(metaclass=SimpleTestMeta):

    pretf = command.PretfCommand()
    tf = command.TerraformCommand()

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
