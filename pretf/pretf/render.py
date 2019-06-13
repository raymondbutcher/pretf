from pathlib import Path, PurePath
from typing import Any, Dict, Generator, Iterable, List, Union

from .exceptions import FunctionNotFoundError
from .util import import_file
from .variables import (
    TerraformVariableStore,
    get_variable_definitions_from_block,
    get_variable_values_from_block,
)


class Block(Iterable):
    def __init__(self, block_type: str, labels: List[str], body: Any):
        self._block_type = block_type
        self._labels = labels
        self._body = body

    def __iter__(self) -> Generator[tuple, None, None]:
        if self._labels:
            result: dict = {}
            here = result
            for label in self._labels[:-1]:
                here[label] = {}
                here = here[label]
            here[self._labels[-1]] = self._body
        else:
            result = self._body
        yield (self._block_type, result)

    def __getattr__(self, name) -> Union["Interpolated", str]:
        if self._block_type == "resource":
            parts = list(self._labels)
        elif self._block_type == "variable":
            parts = ["var"]
        elif self._block_type == "provider":
            parts = list(self._labels)
            if name == "alias":
                if self._body:
                    alias = self._body.get("alias")
                    if alias:
                        parts.append(alias)
                return ".".join(parts)
        elif self._block_type == "locals":
            parts = ["local"]
        else:
            parts = [self._block_type] + list(self._labels)
        parts.append(name)
        return Interpolated(".".join(parts))

    __getitem__ = __getattr__

    def __repr__(self) -> str:
        parts = [self._block_type]
        parts.extend(self._labels)
        if self._body is not None:
            parts.extend(self._body)
        return f"block({', '.join(repr(part) for part in parts)})"

    def __str__(self) -> str:
        return ".".join([self._block_type] + self._labels)


class Interpolated:
    def __init__(self, value: str):
        self.__value = value

    def __eq__(self, other: Any) -> bool:
        return str(self) == other

    def __getattr__(self, attr: str) -> "Interpolated":
        return type(self)(self.__value + "." + attr)

    def __repr__(self) -> str:
        return f"Interpolated({repr(self.__value)})"

    def __str__(self) -> str:
        return "${" + self.__value + "}"


class Renderer:
    def __init__(self, files_to_create: Dict[str, Path]):
        # These are all of the files that will be created.
        self.files_to_create = files_to_create

        # Variables will be populated from environment variables,
        # command line arguments, and files, as per standard Terraform
        # behaviour. They will also be populated as files get created.
        self.variables = TerraformVariableStore(
            files_to_create=files_to_create, process_jobs=self.process_jobs
        )

        # These are all of the jobs to create files.
        self.jobs: List[RenderJob] = []
        for file_path in self.files_to_create.values():
            job = RenderJob(path=file_path, variables=self.variables)
            self.jobs.append(job)

        # This will be populated with blocks from each file being created.
        self.done: List[RenderJob] = []

    def process_jobs(self, until=None) -> None:
        while self.jobs:
            if until and until in self.variables:
                break
            job = self.jobs.pop()
            done = job.run()
            if done:
                self.done.append(job)
            else:
                self.jobs.append(job)

    def render(self) -> Dict[Path, Union[dict, List[dict]]]:
        self.process_jobs()
        results = {}
        for job in self.done:
            results[job.output_path] = job.contents()
        return results


class RenderJob:
    def __init__(self, path, variables):

        self.path = path
        self.variables = variables

        # Create a var object to pass into the file's generator function.
        # This allows attribute and dict access to the variables.
        var = variables.proxy(path)

        # Load the file and start the generator.
        with import_file(path) as module:
            if not hasattr(module, "pretf_blocks"):
                raise FunctionNotFoundError(
                    f"create: {path} does not have a 'pretf_blocks' function"
                )
            self.gen = module.pretf_blocks(var)

        self.done = False
        self.output_path = path.with_suffix(".json")
        self.output_name = self.output_path.name
        self.return_value = None

        self.blocks = []

    def contents(self) -> Union[dict, List[dict]]:
        if self.output_name.endswith(".tfvars.json"):
            merged = {}
            for block in self.blocks:
                for name, value in block.items():
                    merged[name] = value
            return merged
        else:
            return self.blocks

    def process_tf_block(self, block: dict) -> None:
        for var in get_variable_definitions_from_block(block, self.path.name):
            # Add the variable definition. This doesn't necessarily
            # make it available to use, because a tfvars file may
            # populate it later.
            self.variables.add(var)

    def process_tfvars_block(self, block: dict) -> None:
        # Only populate the variable store with values in this file
        # if it is waiting for this file. It is possible to generate
        # tfvars files that don't get used as a source for values.
        if self.variables.tfvars_waiting_for(self.output_name):
            for var in get_variable_values_from_block(block, source=self.path.name):
                # Add the variable value. Raise an error if it changes
                # the value, because it could result in Pretf using
                # the old value and Terraform using the new one.
                self.variables.add(var, allow_change=False)

    def run(self) -> bool:

        try:
            yielded = self.gen.send(self.return_value)
        except StopIteration:
            self.variables.file_created(self.output_name)
            return True

        self.return_value = yielded

        for block in unwrap_yielded(yielded):

            if self.output_name.endswith(".tfvars.json"):
                self.process_tfvars_block(block)
            else:
                self.process_tf_block(block)

            self.blocks.append(block)

        return False


def json_default(obj: Any) -> Any:
    if isinstance(obj, (Interpolated, PurePath)):
        return str(obj)
    raise TypeError(repr(obj))


def unwrap_yielded(
    yielded: Union[Block, dict, Iterable]
) -> Generator[dict, None, None]:
    if isinstance(yielded, Block):
        yield dict(iter(yielded))
    elif isinstance(yielded, dict):
        yield yielded
    else:
        yield from yielded
