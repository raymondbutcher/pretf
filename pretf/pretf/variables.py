import os
import shlex
import sys
from collections import defaultdict
from pathlib import Path
from threading import Event, Lock
from typing import Any, Dict, Generator, List, Set, Union

from . import log
from .exceptions import (
    VariableAlreadyDefinedError,
    VariableNotConsistentError,
    VariableNotDefinedError,
    VariableNotPopulatedError,
)
from .parser import (
    parse_environment_variable_for_variables,
    parse_json_file_for_blocks,
    parse_tf_file_for_variables,
    parse_tfvars_file_for_variables,
)


class VariableProxy:
    def __init__(self, store: "VariableStore", consumer: Any):
        self._store = store
        self._consumer = consumer

    def __contains__(self, name: str) -> bool:
        return name in self._store

    def __getattr__(self, name: str) -> Any:
        return self._store.get(name, self._consumer)

    __getitem__ = __getattr__


class VariableStore:
    def __init__(self) -> None:
        self._allow_changes = True
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
            if not self._allow_changes and var.name in self._values:
                old_var = self._values[var.name]
                if var.value != old_var.value:
                    raise VariableNotConsistentError(old_var=old_var, new_var=var)
            self._values[var.name] = var
        else:
            raise TypeError(var)

    def enable_changes(self) -> None:
        self._allow_changes = True

    def enable_defaults(self) -> None:
        self._allow_defaults = True

    def disable_changes(self) -> None:
        self._allow_changes = False

    def disable_defaults(self) -> None:
        self._allow_defaults = False

    def get(self, name: str, consumer: Any) -> Any:
        if name in self._definitions:
            if name in self._values:
                return self._values[name].value
            if self._allow_defaults:
                if self._definitions[name].has_default:
                    return self._definitions[name].default
            raise VariableNotPopulatedError(name, consumer)
        raise VariableNotDefinedError(name, consumer)

    def proxy(self, consumer: Any) -> VariableProxy:
        return VariableProxy(store=self, consumer=consumer)


class TerraformVariableStore(VariableStore):
    def __init__(self, files_to_create: dict) -> None:
        super().__init__()  # type: ignore
        self._files_to_create = files_to_create
        self._files_done: Set[Path] = set()
        self._tfvars_waiting: Set[Path] = set()
        self._events: Dict[str, List[Event]] = defaultdict(list)
        self._lock = Lock()

    def _blocked_threads(self) -> int:
        count = 0
        for events in self._events.values():
            for event in events:
                if not event.is_set():
                    count += 1
        return count

    def _threads(self) -> int:
        return len(self._files_to_create) - len(self._files_done)

    def _unblock(self, name: str) -> None:
        events = self._events[name]
        while events:
            event = events.pop()
            event.set()

    def abort(self) -> None:
        with self._lock:
            for name in self._events:
                self._unblock(name)

    def add(self, var: Union["VariableDefinition", "VariableValue"]) -> None:
        with self._lock:

            super().add(var)

            # If this variable is ready,
            # unblock any threads waiting for it.
            if var.name in self:
                self._unblock(var.name)

    def file_done(self, path: Path) -> None:
        with self._lock:

            self._files_done.add(path)
            self._tfvars_waiting.discard(path)

            # If there are no tfvars files left to be rendered,
            # then allow the default values to be used.
            if not self._tfvars_waiting:
                self.enable_defaults()

                # Unblock other threads waiting for variables with default values.
                for var in self._definitions.copy().values():
                    if var.has_default:
                        self._unblock(var.name)

            # If all other threads are blocked waiting for variables then
            # there is a deadlock. In that case unblock every variable so
            # threads can continue and fail.
            blocked_threads = self._blocked_threads()
            if blocked_threads and blocked_threads >= self._threads():
                for name in self._events:
                    self._unblock(name)

    def get(self, name: str, consumer: Any) -> Any:
        with self._lock:

            # Return the value if the variable is ready.
            if name in self:
                return super().get(name, consumer)

            # If all other threads are blocked and waiting for variables,
            # then having this thread wait for a variable would cause a deadlock.
            # In that case just try to return the value and let it fail.
            if self._blocked_threads() + 1 >= self._threads():
                return super().get(name, consumer)

            # Create an event that can be used to block this thread
            # until the variable is ready.
            event = Event()
            self._events[name].append(event)

        # Block this thread until another thread makes the variable ready
        # or another thread detects a deadlock and unblocks all threads.
        event.wait()

        # Try to return the value.
        # If there was a deadlock then this will fail.
        return super().get(name, consumer)

    def tfvars_wait_for(self, path: Path) -> None:
        if path not in self._files_done:
            self._tfvars_waiting.add(path)
            self.disable_defaults()

    def tfvars_waiting_for(self, path: Path) -> bool:
        return path in self._tfvars_waiting

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

        self.disable_defaults()
        self.enable_changes()

        auto_tfvars_files = set()
        default_tfvars_files = set()
        tf_files = set()

        target_dir = next(iter(self._files_to_create.keys())).parent

        future_files: Set[Path] = set()
        future_files.update(target_dir.iterdir())
        future_files.update(self._files_to_create.keys())
        for path in future_files:
            name = path.name
            if name.endswith(".auto.tfvars") or name.endswith(".auto.tfvars.json"):
                auto_tfvars_files.add(path)
            elif name in ("terraform.tfvars", "terraform.tfvars.json"):
                default_tfvars_files.add(path)
            elif name.endswith(".tf") or name.endswith(".tf.json"):
                tf_files.add(path)

        # Load variable definitions.
        for path in tf_files:
            if path not in self._files_to_create:
                for var in get_variables_from_file(path):
                    self.add(var)

        # Load variable values.
        # 1. Environment variables.
        for key, value in os.environ.items():
            if key.startswith("TF_VAR_"):
                parsed = parse_environment_variable_for_variables(key, value)
                for name, value in parsed.items():
                    var = VariableValue(name=name, value=value, source=key)
                    self.add(var)

        # 2. The terraform.tfvars file, if present.
        # 3. The terraform.tfvars.json file, if present.
        for path in sorted(default_tfvars_files):
            if path in self._files_to_create:
                self.tfvars_wait_for(path)
            else:
                for var in get_variables_from_file(path):
                    self.add(var)

        # 4. Any *.auto.tfvars or *.auto.tfvars.json files,
        #    processed in lexical order of their filenames.
        for path in sorted(auto_tfvars_files):
            if path in self._files_to_create:
                self.tfvars_wait_for(path)
            else:
                for var in get_variables_from_file(path):
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
                var_file = Path(os.path.abspath(arg[10:])).resolve()
                for target_path in self._files_to_create.keys():
                    if target_path.resolve() == var_file:
                        self.tfvars_wait_for(target_path)
                        break
                else:
                    for var in get_variables_from_file(var_file):
                        self.add(var)

        self.disable_changes()
        if not self._tfvars_waiting:
            self.enable_defaults()


class VariableDefinition:
    def __init__(self, name: str, source: Any, **kwargs: dict) -> None:
        self.name = name
        self.source = str(source)
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
    def __init__(self, name: str, value: Any, source: Any) -> None:
        self.name = name
        self.value = value
        self.source = str(source)

    def __iter__(self) -> Generator[tuple, None, None]:
        yield ("name", self.name)
        yield ("value", self.value)
        yield ("source", self.source)


def get_variable_definitions_from_block(
    block: dict, source: Any
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
    block: dict, source: Any
) -> Generator[VariableValue, None, None]:
    for name, value in block.items():
        yield VariableValue(name=name, value=value, source=source)


def get_variables_from_file(
    path: Path,
) -> Generator[Union[VariableDefinition, VariableValue], None, None]:
    try:
        if path.name.endswith(".tf"):
            yield from get_variables_from_tf_file(path)
        elif path.name.endswith(".tfvars"):
            yield from get_variables_from_tfvars_file(path)
        elif path.name.endswith(".tf.json"):
            yield from get_variables_from_tf_json_file(path)
        elif path.name.endswith(".tfvars.json"):
            yield from get_variables_from_tfvars_json_file(path)
        else:
            raise ValueError(f"Unexpected file extension: {path.name}")
    except Exception:
        log.bad(f"Error loading variables from {path}")
        raise


def get_variables_from_tf_file(path: Path) -> Generator[VariableDefinition, None, None]:
    blocks = parse_tf_file_for_variables(path)
    for block in blocks:
        yield from get_variable_definitions_from_block(block, path.name)


def get_variables_from_tfvars_file(path: Path) -> Generator[VariableValue, None, None]:
    blocks = parse_tfvars_file_for_variables(path)
    for block in blocks:
        yield from get_variable_values_from_block(block, path.name)


def get_variables_from_tf_json_file(
    path: Path,
) -> Generator[VariableDefinition, None, None]:
    blocks = parse_json_file_for_blocks(path)
    for block in blocks:
        yield from get_variable_definitions_from_block(block, path.name)


def get_variables_from_tfvars_json_file(
    path: Path,
) -> Generator[VariableValue, None, None]:
    blocks = parse_json_file_for_blocks(path)
    for block in blocks:
        yield from get_variable_values_from_block(block, path.name)
