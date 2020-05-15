import inspect
import os
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path, PurePath
from threading import Thread
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from . import log
from .blocks import Block, Interpolated
from .exceptions import FunctionNotFoundError
from .util import find_workflow_path, import_file
from .variables import (
    TerraformVariableStore,
    VariableProxy,
    VariableValue,
    get_variable_definitions_from_block,
)


class PathProxy:
    def __init__(self) -> None:
        self.cwd = Path.cwd()
        self.module = Path(".")
        self.root = Path(".")

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def top(self) -> Path:
        """
        Returns the directory containing the pretf.workflow.py file,
        or the current directory if there is none.

        """

        workflow_path = find_workflow_path()
        if workflow_path:
            return workflow_path.parent
        else:
            return self.cwd


def render_files(
    files_to_create: Dict[Path, Path]
) -> Dict[Path, Union[dict, List[dict]]]:

    variables = TerraformVariableStore(files_to_create=files_to_create)
    variables.load()

    threads = []
    for target_path, source_path in files_to_create.items():
        thread = RenderThread(
            source_path=source_path, target_path=target_path, variables=variables
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        try:
            thread.join()
        except KeyboardInterrupt:
            variables.abort()
            thread.join()

    results = {}
    for thread in threads:
        if thread.error:
            raise thread.error
        results[thread.target_path] = thread.contents()
    return results


class RenderThread(Thread):
    def __init__(
        self, source_path: Path, target_path: Path, variables: TerraformVariableStore
    ):

        super().__init__()

        self.source_path = source_path
        self.target_path = target_path
        self.target_name = target_path.name
        self.variables = variables

        self.error: Optional[Exception] = None
        self.is_tfvars = self.target_name.endswith(".tfvars.json")
        self.return_value = None

        # Load the file and start the generator.
        with import_file(source_path) as module:

            if self.is_tfvars:
                func_name = "pretf_variables"
            else:
                func_name = "pretf_blocks"

            if not hasattr(module, func_name):
                raise FunctionNotFoundError(
                    f"create: {source_path} does not have a {repr(func_name)} function"
                )

            # Call the pretf_* function, passing in "path", "terraform" and "var" if required.
            var_proxy = variables.proxy(consumer=self.source_path)
            self.gen = call_pretf_function(
                func=getattr(module, func_name), var=var_proxy
            )

        self.blocks: List[dict] = []

    def contents(self) -> Union[dict, List[dict]]:
        if self.is_tfvars:
            merged = {}
            for block in self.blocks:
                for name, value in block.items():
                    merged[name] = value
            return merged
        else:
            return self.blocks

    def process_tf_block(self, block: dict) -> None:
        for var in get_variable_definitions_from_block(block, source=self.source_path):
            # Add the variable definition. This doesn't necessarily
            # make it available to use, because a tfvars file may
            # populate it later.
            self.variables.add(var)

    def process_tfvars_dict(self, values: dict) -> None:
        # Only populate the variable store with values in this file
        # if it is waiting for this file. It is possible to generate
        # tfvars files that don't get used as a source for values.
        if self.variables.tfvars_waiting_for(self.target_path):
            for name, value in values.items():
                var = VariableValue(name=name, value=value, source=self.source_path)
                self.variables.add(var)

    def run(self) -> None:
        try:

            while True:

                try:
                    yielded = self.gen.send(self.return_value)
                except StopIteration:
                    break

                self.return_value = yielded

                if self.is_tfvars:
                    if not isinstance(yielded, dict):
                        raise TypeError(
                            f"expected dict to be yielded but got {repr(yielded)}"
                        )
                    self.process_tfvars_dict(yielded)
                    self.blocks.append(yielded)
                else:
                    for block in unwrap_yielded(yielded):

                        self.process_tf_block(block)
                        self.blocks.append(block)

        except Exception as error:

            log.bad(f"create: {self.target_name} could not be processed")
            self.error = error

        finally:

            # Tell the variable store that the file is done,
            # whether it was successful or not, so it can
            # unblock other threads if necessary.
            self.variables.file_done(self.target_path)


class TerraformProxy:
    @property  # type: ignore
    @lru_cache(maxsize=None)
    def workspace(self) -> str:
        workspace = os.getenv("TF_WORKSPACE")
        if not workspace:
            cwd = Path.cwd()
            try:
                workspace = (cwd / ".terraform" / "environment").read_text()
            except FileNotFoundError:
                workspace = "default"
        return workspace


def call_pretf_function(
    func: Callable, var: Optional[VariableProxy] = None, context: Optional[dict] = None
) -> Any:
    kwargs: Dict[str, Any] = context or {}
    sig = inspect.signature(func)
    if "path" in sig.parameters:
        kwargs["path"] = PathProxy()
    if "terraform" in sig.parameters:
        kwargs["terraform"] = TerraformProxy()
    if "var" in sig.parameters and var is not None:
        kwargs["var"] = var
    return func(**kwargs)


def json_default(obj: Any) -> Any:
    if isinstance(obj, (Block, Interpolated, PurePath)):
        return str(obj)
    raise TypeError(repr(obj))


def unwrap_yielded(
    yielded: Union[Block, dict, Iterable], **kwargs: Any
) -> Generator[dict, None, None]:
    if isinstance(yielded, Block):
        yield dict(iter(yielded))
    elif isinstance(yielded, dict):
        yield yielded
    else:
        root = kwargs.get("root", yielded)
        parent = kwargs.get("parent", object())
        if isinstance(yielded, Iterable) and yielded != parent:
            for nested in yielded:
                yield from unwrap_yielded(nested, parent=yielded, root=root)
        else:
            raise TypeError(
                f"expected block to be yielded but got {repr(kwargs.get('root', yielded))}"
            )
