import os
import shlex
import sys
from pathlib import Path
from typing import Any, Callable, Generator, Set, Union

from .exceptions import (
    VariableAlreadyDefinedError,
    VariableNotConsistentError,
    VariableNotDefinedError,
    VariableNotPopulatedError,
)
from .parser import (
    parse_json_file_for_blocks,
    parse_tf_file_for_variables,
    parse_tfvars_file_for_variables,
)
from .util import once


class VariableProxy:
    def __init__(self, store: "VariableStore", consumer: str):
        self._store = store
        self._consumer = consumer

    def __contains__(self, name: str) -> bool:
        return name in self._store

    def __getattr__(self, name: str) -> Any:
        return self._store.get(name, self._consumer)

    __getitem__ = __getattr__


class VariableStore:
    def __init__(self) -> None:
        self._allow_defaults = True
        self._definitions: dict = {}
        self._values: dict = {}

    def __contains__(self, name: str) -> bool:
        if name in self._definitions:
            if name in self._values:
                return True
            if self._allow_defaults:
                if self._definitions[name].has_default:
                    return True
        return False

    def add(self, var: Union["VariableDefinition", "VariableValue"]) -> None:
        if isinstance(var, VariableDefinition):
            if var.name in self._definitions:
                old_var = self._definitions[var.name]
                raise VariableAlreadyDefinedError(old_var=old_var, new_var=var)
            self._definitions[var.name] = var
        elif isinstance(var, VariableValue):
            self._values[var.name] = var
        else:
            raise TypeError(var)

    def enable_defaults(self) -> None:
        self._allow_defaults = True

    def disable_defaults(self) -> None:
        self._allow_defaults = False

    def get(self, name: str, consumer: str) -> Any:
        if name in self._definitions:
            if name in self._values:
                return self._values[name].value
            if self._allow_defaults:
                if self._definitions[name].has_default:
                    return self._definitions[name].default
            raise VariableNotPopulatedError(name, consumer)
        raise VariableNotDefinedError(name, consumer)

    def proxy(self, consumer: str) -> VariableProxy:
        return VariableProxy(store=self, consumer=consumer)


class TerraformVariableStore(VariableStore):
    def __init__(self, files_to_create: dict, process_jobs: Callable) -> None:
        super().__init__()  # type: ignore
        self._files_to_create = files_to_create
        self._files_created: Set[str] = set()
        self._tfvars_waiting: Set[str] = set()
        self._process_jobs = process_jobs

    def add(
        self,
        var: Union["VariableDefinition", "VariableValue"],
        allow_change: bool = True,
    ) -> None:
        # Ensure Terraform variables are loaded before anything from Pretf,
        # because there is a loading order that needs to be followed,
        # and Pretf values come afterwards.
        self.load()

        # This check is used to prevent changing variables values in Pretf,
        # to ensure that Pretf and Terraform always have consistent values.
        if isinstance(var, VariableValue):
            if not allow_change and var.name in self._values:
                old_var = self._values[var.name]
                if var.value != old_var.value:
                    raise VariableNotConsistentError(old_var=old_var, new_var=var)

        super().add(var)

    def file_created(self, name: str) -> None:
        self._files_created.add(name)
        self._tfvars_waiting.discard(name)
        if not self._tfvars_waiting:
            self.enable_defaults()

    def tfvars_wait_for(self, name: str) -> None:
        if name not in self._files_created:
            self._tfvars_waiting.add(name)
            self.disable_defaults()

    def tfvars_waiting_for(self, name: str) -> bool:
        self.load()
        return name in self._tfvars_waiting

    def get(self, name: str, consumer: str) -> Any:
        self.load()
        self._process_jobs(until=name)
        return super().get(name, consumer)

    @once
    def load(self) -> None:
        """
        Load Terraform variables from various sources.

        From https://www.terraform.io/docs/configuration/variables.html

        Terraform loads variables in the following order,
        with later sources taking precedence over earlier ones:

        * Environment variables
        * The terraform.tfvars file, if present.
        * The terraform.tfvars.json file, if present.
        * Any *.auto.tfvars or *.auto.tfvars.json files, processed in lexical order of their filenames.
        * Any -var and -var-file options on the command line, in the order they are provided.

        """

        auto_tfvars_file_names = set()
        default_tfvars_file_names = set()
        tf_file_names = set()

        future_names = list(os.listdir()) + list(self._files_to_create.keys())
        for name in future_names:

            if name.endswith(".auto.tfvars") or name.endswith(".auto.tfvars.json"):
                auto_tfvars_file_names.add(name)
            elif name in ("terraform.tfvars", "terraform.tfvars.json"):
                default_tfvars_file_names.add(name)
            elif name.endswith(".tf") or name.endswith(".tf.json"):
                tf_file_names.add(name)

        # Load variable definitions.
        for name in tf_file_names:
            if name not in self._files_to_create:
                for var in get_variables_from_file(Path(name)):
                    self.add(var)

        # Load variable values.
        # 1. Environment variables.
        for key, value in os.environ.items():
            if key.startswith("TF_VAR_"):
                var = VariableValue(name=key[7:], value=value, source=key)
                self.add(var)

        # 2. The terraform.tfvars file, if present.
        # 3. The terraform.tfvars.json file, if present.
        for name in sorted(default_tfvars_file_names):
            if name in self._files_to_create:
                self.tfvars_wait_for(name)
            else:
                for var in get_variables_from_file(Path(name)):
                    self.add(var)

        # 4. Any *.auto.tfvars or *.auto.tfvars.json files,
        #    processed in lexical order of their filenames.
        for name in sorted(auto_tfvars_file_names):
            if name in self._files_to_create:
                self.tfvars_wait_for(name)
            else:
                for var in get_variables_from_file(Path(name)):
                    self.add(var)

        # 5. Any -var and -var-file options on the command line,
        #    in the order they are provided.
        for arg in sys.argv[1:]:
            if arg.startswith("-var="):
                var_string = shlex.split(arg[5:])[0]
                name, value = var_string.split("=", 1)
                var = VariableValue(name=name, value=value, source=arg)
                self.add(var)
            elif arg.startswith("-var-file="):
                path = Path(os.path.abspath(arg[10:]))
                will_create = False
                if os.path.abspath(path.parent) == os.path.abspath("."):
                    if path.name in self._files_to_create:
                        will_create = True
                if will_create:
                    self.tfvars_wait_for(name)
                else:
                    for var in get_variables_from_file(path):
                        self.add(var)


class VariableDefinition:
    def __init__(self, name: str, source: str, **kwargs: dict) -> None:
        self.name = name
        self.source = source
        self.has_default = False
        for key, value in kwargs.items():
            if key == "default":
                self.has_default = True
                self.default = value
            else:
                raise TypeError(
                    f"{self.__class__.__name__}() got an unexpected keyword argument {repr(key)}"
                )

    def __iter__(self) -> Generator[tuple, None, None]:
        yield ("name", self.name)
        if hasattr(self, "default"):
            yield ("default", self.default)
        yield ("source", self.source)


class VariableValue:
    def __init__(self, name: str, value: Any, source: str) -> None:
        self.name = name
        self.value = value
        self.source = source

    def __iter__(self) -> Generator[tuple, None, None]:
        yield ("name", self.name)
        yield ("value", self.value)
        yield ("source", self.source)


def get_variable_definitions_from_block(
    block: dict, source: str
) -> Generator[VariableDefinition, None, None]:

    if "variable" not in block:
        return

    variable = block["variable"]

    if isinstance(variable, list):
        variables = variable
    elif isinstance(variable, dict):
        variables = [variable]
    elif isinstance(variable, str):
        raise ValueError(
            f"invalid variable, possibly missing body in block() call: {repr(block)}"
        )
    else:
        raise ValueError(f"invalid variable: {repr(block)}")

    for variable in variables:
        for name, block in variable.items():
            kwargs = {"name": name, "source": source}
            if "default" in block:
                kwargs["default"] = block["default"]
            yield VariableDefinition(**kwargs)


def get_variable_values_from_block(
    block: dict, source: str
) -> Generator[VariableValue, None, None]:
    for name, value in block.items():
        yield VariableValue(name=name, value=value, source=source)


def get_variables_from_file(
    path: Path
) -> Generator[Union[VariableDefinition, VariableValue], None, None]:
    if path.name.endswith(".tf"):
        yield from get_variables_from_tf_file(path)
    elif path.name.endswith(".tfvars"):
        yield from get_variables_from_tfvars_file(path)
    elif path.name.endswith(".tf.json"):
        yield from get_variables_from_tf_json_file(path)
    elif path.name.endswith(".tfvars.json"):
        yield from get_variables_from_tfvars_json_file(path)
    else:
        raise ValueError(path.name)


def get_variables_from_tf_file(path: Path) -> Generator[VariableDefinition, None, None]:
    blocks = parse_tf_file_for_variables(path)
    for block in blocks:
        yield from get_variable_definitions_from_block(block, path.name)


def get_variables_from_tfvars_file(path: Path) -> Generator[VariableValue, None, None]:
    blocks = parse_tfvars_file_for_variables(path)
    for block in blocks:
        yield from get_variable_values_from_block(block, path.name)


def get_variables_from_tf_json_file(
    path: Path
) -> Generator[VariableDefinition, None, None]:
    blocks = parse_json_file_for_blocks(path)
    for block in blocks:
        yield from get_variable_definitions_from_block(block, path.name)


def get_variables_from_tfvars_json_file(
    path: Path
) -> Generator[VariableValue, None, None]:
    blocks = parse_json_file_for_blocks(path)
    for block in blocks:
        yield from get_variable_values_from_block(block, path.name)
