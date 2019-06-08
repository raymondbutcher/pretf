import os
import shlex
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .parser import get_variables_from_block, get_variables_from_file
from .util import import_file


class Block:
    def __init__(self, path, body=None):
        self.__path = path
        self.__body = body or {}

    def __iter__(self):
        result = {}
        if "." in self.__path:
            here = result
            for part in self.__path.split("."):
                here[part] = {}
                here = here[part]
            here.update(self.__body)
        else:
            result[self.__path] = self.__body
        for key, value in result.items():
            yield (key, value)

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, key):

        parts = self.__path.split(".")

        if parts[0] == "resource":
            parts.pop(0)
        elif parts[0] == "variable":
            parts[0] = "var"

        parts.append(key)

        return Interpolated(".".join(parts))

    def __repr__(self):
        return f"tf({repr(self.__path)}, {repr(self.__body)})"

    def __str__(self):
        return self.__path


class Collection:
    def __init__(self, blocks, outputs):
        self.__blocks = blocks
        self.__outputs = outputs

    def __getattr__(self, name):
        if name in self.__outputs:
            return self.__outputs[name]
        raise AttributeError(f"output not defined: {name}")

    def __iter__(self):
        for value in self.__blocks:
            yield value


class Interpolated:
    def __init__(self, value):
        self.__value = value

    def __eq__(self, other):
        return str(self) == other

    def __getattr__(self, attr):
        return type(self)(self.__value + "." + attr)

    def __repr__(self):
        return f"Interpolated({repr(self.__value)})"

    def __str__(self):
        return "${" + self.__value + "}"


class Renderer:
    def __init__(self):

        # These will be populated with Terraform variables.
        self.variable_defaults = {}
        self.variable_files = set()
        self.variable_from = {}
        self.variable_names = set()
        self.variable_values = {}

        # Keep track of remaining tfvars files that need to be generated
        # to determine whether variable defaults can be used or not.
        self.tfvars_remaining = 0

        # This will be populated with any files that have tried
        # to use a variable that is not defined or populated yet.
        self.blocked_files = defaultdict(list)

        # This will be populated with any files that are not waiting
        # on a variable, so they are able to be generated.
        self.unblocked_files = []
        self.return_values = {}

        # Results from processed files go here.
        self.results = defaultdict(list)

    @lru_cache()
    def file_paths(self):
        return sorted(Path().iterdir())

    def get_variable_value(self, name, path):

        self.load_variables()

        if name not in self.variable_names:
            raise VariableNotDefined(name, path)

        if name in self.variable_values:
            return self.variable_values[name]

        if not self.tfvars_remaining:
            if name in self.variable_defaults:
                return self.variable_defaults[name]

        raise VariableNotPopulated(name, path)

    @lru_cache()
    def load_variables(self):
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

        If Pretf is used to generate a *.tfvars.json file, and it contains a variable that was already
        provided by any of the above sources, and the value differs, then an error will be raised.

        """

        # Load variable definitions.
        for file_path in self.file_paths():
            file_name = file_path.name
            if file_name.endswith(".tf"):
                for var in get_variables_from_file(file_path):
                    var_name = var["name"]
                    self.variable_names.add(var_name)
                    if "default" in var:
                        self.variable_defaults[var_name] = var["default"]

        # Load variable values.
        # 1. Environment variables.
        for key, value in os.environ.items():
            if key.startswith("TF_VAR_"):
                name = key[7:]
                self.variable_values[name] = value
                self.variable_from[name] = key

        # 2. The terraform.tfvars file, if present.
        # 3. The terraform.tfvars.json file, if present.
        for file_path in self.file_paths():
            if file_path.name in ("terraform.tfvars", "terraform.tfvars.json"):
                for var in get_variables_from_file(file_path):
                    name, value = var["name"], var["value"]
                    self.variable_values[name] = value
                    self.variable_from[name] = file_path.name

        # 4. Any *.auto.tfvars or *.auto.tfvars.json files,
        #    processed in lexical order of their filenames.
        for file_path in self.file_paths():
            file_name = file_path.name
            if file_name.endswith(".auto.tfvars") or file_name.endswith(
                ".auto.tfvars.json"
            ):
                for var in get_variables_from_file(file_path):
                    name, value = var["name"], var["value"]
                    self.variable_values[name] = value
                    self.variable_from[name] = file_path.name

        # 5. Any -var and -var-file options on the command line,
        #    in the order they are provided.
        for arg in sys.argv[1:]:
            if arg.startswith("-var="):
                var_string = shlex.split(arg[5:])[0]
                name, value = var_string.split("=", 1)
                self.variable_values[name] = value
                self.variable_from[name] = arg
            elif arg.startswith("-var-file="):
                file_path = Path(arg[10:])
                self.variable_files.add(file_path)
                for var in get_variables_from_file(file_path):
                    name, value = var["name"], var["value"]
                    self.variable_values[name] = value
                    self.variable_from[name] = arg

    def process_file(self):

        file_item = self.unblocked_files.pop()
        file_path, file_gen = file_item

        return_value = self.return_values.get(file_path)
        try:
            yielded = file_gen.send(return_value)
        except StopIteration:
            if file_path.name.endswith(".tfvars.py"):
                self.tfvars_remaining -= 1
            return

        self.return_values[file_path] = yielded
        self.unblocked_files.append(file_item)

        for block in unwrap_yielded(yielded):

            self.results[file_path].append(block)

            if file_path.name.endswith(".tfvars.py"):
                self.process_tfvars_block(file_path, block)
            else:
                self.process_tf_block(file_path, block)

    def process_files(self):
        while self.unblocked_files:
            self.process_file()

    def process_tf_block(self, file_path, block):
        """
        Read variables from this file and resume
        any files that are waiting for them.

        """

        for var in get_variables_from_block(block):

            name = var["name"]

            self.variable_names.add(name)

            if "default" in var:
                self.variable_defaults[name] = var["default"]

            try:
                value = self.get_variable_value(name, file_path)
            except VariableError:
                pass
            else:
                self.resume_files(name, value)

    def process_tfvars_block(self, file_path, block):
        """
        Read variables from this file and resume
        any files that are waiting for them.

        """

        # Only process this file if it will also be used by
        # Terraform as a variable source. Otherwise, Pretf
        # and Terraform could have inconsistent values.
        if file_path.name == "terraform.tfvars.py":
            pass
        elif file_path.name.endswith(".auto.tfvars.py"):
            pass
        else:
            output_file_path = file_path.with_suffix(".json").resolve()
            for var_file_path in self.variable_files:
                if var_file_path.resolve() == output_file_path:
                    break
            else:
                # Don't parse this file
                return

        for name, value in block.items():

            # Check that we're not changing a variable value
            # as this could result in Python code using one
            # value and Terraform using another.
            if name in self.variable_values:
                if self.variable_values[name] != value:
                    var_from = self.variable_from[name]
                    raise VariableNotConsistent(name, var_from, file_path)
            else:
                # Otherwise, set the variable value and resume
                # any files that are waiting for it.
                self.variable_values[name] = value
                self.resume_files(name, value)

    def render(self):
        # Find files to process.
        for file_path in self.file_paths():
            file_name = file_path.name
            if file_name.endswith(".tf.py") or file_name.endswith(".tfvars.py"):
                var = VariableProxy(self, file_path)
                with import_file(file_path) as module:
                    file_gen = module.terraform(var)
                file_item = [file_path, file_gen]
                self.unblocked_files.append(file_item)
                if file_name.endswith(".tfvars.py"):
                    self.tfvars_remaining += 1

        # Process all files one block at a time.
        self.process_files()

        # Raise an exception if any files could not be generated
        # due to problems with variables.
        variable_error = VariableError()
        for var_name, file_items in self.blocked_files.items():
            for file_item in file_items:
                file_path, file_gen = file_item
                if var_name in self.variable_names:
                    variable_error.add(VariableNotPopulated(var_name, file_path))
                else:
                    variable_error.add(VariableNotDefined(var_name, file_path))
        if variable_error.errors:
            raise variable_error

        return self.results

    def resume_files(self, var_name, var_value):
        while self.blocked_files[var_name]:
            file_item = self.blocked_files[var_name].pop()
            file_path, file_gen = file_item
            self.return_values[file_path] = var_value
            self.unblocked_files.append(file_item)


class VariableError(Exception):
    def __init__(self):
        self.errors = []

    def add(self, error):
        self.errors.append(error)

    def __str__(self):
        errors = "\n".join(f"  {error}" for error in self.errors)
        return f"\n{errors}"


class VariableNotConsistent(VariableError):
    def __init__(self, name, other, path):
        self.name = name
        self.other = other
        self.path = path

    def __str__(self):
        return f"create: {self.path} cannot set value for var.{self.name} because {self.other} set it with a different value"


class VariableNotDefined(VariableError):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return f"create: {self.path} cannot access var.{self.name} because it has not been defined"


class VariableNotPopulated(VariableError):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return (
            f"create: {self.path} cannot access var.{self.name} because it has no value"
        )


class VariableProxy:
    def __init__(self, renderer, file_path):
        self.__renderer = renderer
        self.__file_path = file_path

    def __getattr__(self, name):
        self.__renderer.process_files()
        return self.__renderer.get_variable_value(name, self.__file_path)

    __getitem__ = __getattr__


def json_default(obj):
    if isinstance(obj, Interpolated):
        return str(obj)
    raise TypeError(repr(obj))


def unwrap_yielded(yielded):
    if isinstance(yielded, Block):
        yield dict(iter(yielded))
    elif isinstance(yielded, Collection):
        for nested in yielded:
            yield from unwrap_yielded(nested)
    elif isinstance(yielded, dict):
        yield yielded
    else:
        raise TypeError(yielded)
