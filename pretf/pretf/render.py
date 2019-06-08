import os
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .parser import get_variables_from_block
from .util import import_file
from .variables import TerraformVariables, VariableError, VariableNotConsistent


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

        parts = self.__path.split(".")

        if parts[0] == "resource":
            parts.pop(0)
        elif parts[0] == "variable":
            parts[0] = "var"

        parts.append(name)

        return Interpolated(".".join(parts))

    __getitem__ = __getattr__

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
        result = []
        for path in sorted(os.listdir()):
            # Get absolute path without resolving symlinks.
            path = Path(os.path.abspath(path))
            result.append(path)
        return result

    @property
    @lru_cache()
    def variables(self):
        return TerraformVariables(file_paths=self.file_paths())

    def process_file(self):

        file_item = self.unblocked_files.pop()
        file_path, file_gen = file_item

        return_value = self.return_values.get(file_path)
        try:
            yielded = file_gen.send(return_value)
        except StopIteration:
            if self.variables.is_source_file(file_path):
                self.variables.enable_defaults(file_path)
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
        for var in get_variables_from_block(block):
            self.variables.add(var)
            try:
                value = self.variables.get_value(var["name"], file_path)
            except VariableError:
                pass
            else:
                self.resume_files(var["name"], value)

    def process_tfvars_block(self, file_path, block):
        if self.variables.is_source_file(file_path):
            for name, value in block.items():

                var = {"name": name, "value": value, "source": file_path.name}
                self.variables.add(var)

                try:
                    existing_value = self.variables.get_value(name, file_path)
                except VariableError:
                    self.variables.set_value(name, value, file_path)
                    self.resume_files(name, value)
                else:
                    if value != existing_value:
                        old_source = self.variables.get_source(name)
                        raise VariableNotConsistent(
                            name, old_source=old_source, new_source=file_path
                        )

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

                if self.variables.is_source_file(file_path):
                    self.variables.disable_defaults(file_path)

        # Process all files one block at a time.
        self.process_files()

        # Raise an exception if any files could not be generated
        # due to problems with variables.
        variable_error = VariableError()
        for var_name, file_items in self.blocked_files.items():
            for file_item in file_items:
                file_path, file_gen = file_item
                try:
                    self.variables.get_value(var_name, file_path)
                except VariableError as error:
                    variable_error.add(error)
                else:
                    raise Exception("how did it get here?")
        if variable_error.errors:
            raise variable_error

        return self.results

    def resume_files(self, var_name, var_value):
        while self.blocked_files[var_name]:
            file_item = self.blocked_files[var_name].pop()
            file_path, file_gen = file_item
            self.return_values[file_path] = var_value
            self.unblocked_files.append(file_item)


class VariableProxy:
    def __init__(self, renderer, file_path):
        self.__renderer = renderer
        self.__file_path = file_path

    def __getattr__(self, name):
        self.__renderer.process_files()
        return self.__renderer.variables.get_value(name, self.__file_path)

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
