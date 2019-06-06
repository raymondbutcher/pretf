import os
import shlex
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .parser import get_variables_from_block, get_variables_from_file
from .util import import_file


class Block:
    def __init__(self, path, body):
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
        return iter(result.items())

    def __getattr__(self, attr):

        parts = self.__path.split(".")

        if parts[0] == "resource":
            parts.pop(0)
        elif parts[0] == "variable":
            parts[0] = "var"

        parts.append(attr)

        return "${" + ".".join(parts) + "}"

    def __repr__(self):
        return f"Block({self})"

    def __str__(self):
        return self.__path


class Renderer:
    def __init__(self):

        # These will be populated with Terraform variables.
        self.variable_loaded = False
        self.variable_names = set()
        self.variable_values = {
            "default": {},
            "env": {},
            "terraform.tfvars": {},
            "terraform.tfvars.json": {},
            "auto": {},
            "cli": {},
        }

        # Keep track of remaining tfvars files that need to be generated
        # to determine whether variable defaults can be used or not.
        self.tfvars_remaining = 0

        # This will be populated with any files that have tried
        # to use a variable that is not defined or populated yet.
        self.blocked_files = defaultdict(list)

        # This will be populated with any files that are not waiting
        # on a variable, so they are able to be generated.
        self.unblocked_files = []
        self.send_queue = {}

        # Results from processed files go here.
        self.results = defaultdict(list)

    def get_variable_value(self, name, path):
        """

        From https://www.terraform.io/docs/configuration/variables.html

        Terraform loads variables in the following order,
        with later sources taking precedence over earlier ones:

        * Environment variables
        * The terraform.tfvars file, if present.
        * The terraform.tfvars.json file, if present.
        * Any *.auto.tfvars or *.auto.tfvars.json files, processed in lexical order of their filenames.
        * Any -var and -var-file options on the command line, in the order they are provided.

        Due to the dynamic nature of Python functions in *.tfvars.py files,
        all of the above sources will take precedence over any values defined
        in *.tfvars.py files.

        """

        self.load_variables()

        if name not in self.variable_names:
            raise VariableNotDefined(name, path)

        for key in ("cli", "auto", "terraform.tfvars.json", "terraform.tfvars", "env"):
            var_holder = self.variable_values[key]
            if name in var_holder:
                return var_holder[name]

        if not self.tfvars_remaining:
            if name in self.variable_values["default"]:
                return self.variable_values["default"][name]

        raise VariableNotPopulated(name, path)

    @lru_cache()
    def paths(self):
        return sorted(Path().iterdir())

    @lru_cache()
    def load_variables(self):

        # Load variable definitions.
        for file_path in self.paths():
            file_name = file_path.name
            if file_name.endswith(".tf"):
                for var in get_variables_from_file(file_path):
                    var_name = var["name"]
                    self.variable_names.add(var_name)
                    if "default" in var:
                        self.variable_values["default"][var_name] = var["default"]

        # Load variable values.
        # 1. Environment variables.
        for key, value in os.environ.items():
            if key.startswith("TF_VAR_"):
                name = key[7:]
                self.variable_values["env"][name] = value

        # 2. The terraform.tfvars file, if present.
        # 3. The terraform.tfvars.json file, if present.
        # 4. Any *.auto.tfvars or *.auto.tfvars.json files,
        #    processed in lexical order of their filenames.
        for file_path in self.paths():
            file_name = file_path.name
            if file_name in ("terraform.tfvars", "terraform.tfvars.json"):
                var_holder = self.variable_values[file_name]
                for var in get_variables_from_file(file_path):
                    var_holder[var["name"]] = var["value"]
            elif file_name.endswith(".auto.tfvars") or file_name.endswith(
                ".auto.tfvars.json"
            ):
                var_holder = self.variable_values["auto"]
                for var in get_variables_from_file(file_path):
                    var_holder[var["name"]] = var["value"]

        # 5. Any -var and -var-file options on the command line,
        #    in the order they are provided.
        var_holder = self.variable_values["cli"]
        for arg in sys.argv[1:]:
            if arg.startswith("-var="):
                var_string = shlex.split(arg[5:])[0]
                name, value = var_string.split("=", 1)
                var_holder[name] = value
            elif arg.startswith("-var-file="):
                file_path = Path(arg[10:])
                for var in get_variables_from_file(file_path):
                    var_holder[var["name"]] = var["value"]

    def process_file(self):

        file_item = self.unblocked_files.pop()
        file_path, file_gen = file_item

        try:
            try:
                return_value = self.send_queue.pop(file_path)
            except KeyError:
                yielded = next(file_gen)
            else:
                yielded = file_gen.send(return_value)
        except StopIteration:
            if file_path.name.endswith(".tfvars.py"):
                self.tfvars_remaining -= 1
            return

        # The file generator yielded a Block (or a raw dictionary,
        # or an invalid value). Add it to the file contents to be
        # written as JSON. Also check if any variables were defined
        # in this block, and use them to resume any blocked generators
        # that are waiting for the variable.

        if isinstance(yielded, Block):
            # Convert the block into a dictionary.
            block = dict(iter(yielded))
        elif isinstance(yielded, dict):
            block = yielded
        else:
            raise TypeError(f"{yielded} in {file_path}")

        # Include this block in the results.
        self.results[file_path].append(block)

        self.send_queue[file_path] = yielded
        self.unblocked_files.append(file_item)

        if file_path.name.endswith(".tfvars.py"):

            if file_path.name == "terraform.tfvars.py":
                var_holder = self.variable_values["terraform.tfvars"]
            elif file_path.name.endswith(".auto.tfvars.py"):
                var_holder = self.variable_values["auto"]
            else:
                var_holder = None

            if var_holder is not None:
                for var_name, var_value in block.items():
                    var_holder[var_name] = var_value
                    self.resume_files(var_name, var_value)

        else:

            # If this block contained a variable, then unblock
            # any files that are blocked by this variable.
            for var in get_variables_from_block(block):

                var_name = var["name"]

                self.variable_names.add(var_name)

                if "default" in var:
                    self.variable_values["default"][var_name] = var["default"]

                try:
                    var_value = self.get_variable_value(var_name, file_path)
                except VariableError:
                    pass
                else:
                    self.resume_files(var_name, var_value)

    def process_files(self):
        while self.unblocked_files:
            self.process_file()

    def render(self):
        # Find files to process.
        for file_path in self.paths():
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
            self.send_queue[file_path] = var_value
            self.unblocked_files.append(file_item)


class VariableError(Exception):
    def __init__(self):
        self.errors = []

    def add(self, error):
        self.errors.append(error)

    def __str__(self):
        errors = "\n".join(f"  {error}" for error in self.errors)
        return f"\n{errors}"


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
