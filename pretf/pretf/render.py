from collections import defaultdict

from .util import import_file
from .variables import (
    TerraformVariableStore,
    VariableError,
    VariableValue,
    get_variables_from_block,
)


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
    def __init__(self, files_to_create):
        # These are all of the files that will be created.
        self.files_to_create = files_to_create

        # This will be populated with any files that have tried
        # to use a variable that is not defined or populated yet.
        self.blocked_files = defaultdict(list)

        # This will be populated with any files that are not waiting
        # on a variable, so they can continue to be created.
        self.unblocked_files = []
        self.return_values = {}

        # Results from processed files go here.
        self.results = defaultdict(list)

        # Variables will be populated from environment variables,
        # command line arguments, and files, as per standard Terraform
        # behaviour. They will also be populated as files get created.
        self.variables = TerraformVariableStore(files_to_create=files_to_create)

    def process_file(self):

        file_item = self.unblocked_files.pop()
        file_path, file_gen = file_item

        return_value = self.return_values.get(file_path)
        try:
            yielded = file_gen.send(return_value)
        except StopIteration:
            output_name = file_path.with_suffix(".json").name
            self.variables.file_created(output_name)
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
        for var in get_variables_from_block(block, file_path.name):
            # Add the variable definition. This doesn't necessarily
            # make it available to use, because a tfvars file may
            # populate it later.
            self.variables.add(var)

            # Resume files waiting for this variable
            # if the variable available to use now.
            if var.name in self.variables:
                value = self.variables.get(var.name, file_path)
                self.resume_files(var.name, value)

    def process_tfvars_block(self, file_path, block):
        # Only populate the variable store with values in this file
        # if it is waiting for this file. It is possible to generate
        # tfvars files that don't get used as a source for values.
        output_name = file_path.with_suffix(".json").name
        if self.variables.tfvars_waiting_for(output_name):
            for name, value in block.items():
                # Add the variable value. Raise an error if it changes
                # the value, because it could result in Pretf using
                # the old value and Terraform using the new one.
                var = VariableValue(name=name, value=value, source=file_path.name)
                self.variables.add(var, allow_change=False)

                # Resume files waiting for this variable.
                self.resume_files(name, value)

    def render(self):
        # Add files to be processed.
        for file_path in self.files_to_create.values():
            var = self.variables.proxy(file_path)
            with import_file(file_path) as module:
                file_gen = module.terraform(var)
            file_item = [file_path, file_gen]
            self.unblocked_files.append(file_item)

        # Process files one block at a time.
        self.process_files()

        # Raise an exception if any files could not be generated
        # due to problems with variables.
        variable_error = VariableError()
        for var_name, file_items in self.blocked_files.items():
            for file_item in file_items:
                file_path, file_gen = file_item
                try:
                    self.variables.get(var_name, file_path)
                except VariableError as error:
                    variable_error.add(error)
                else:
                    raise Exception("how did it get here?")
        if variable_error.errors:
            raise variable_error

        # All files were created successfully.
        return self.results

    def resume_files(self, var_name, var_value):
        while self.blocked_files[var_name]:
            file_item = self.blocked_files[var_name].pop()
            file_path, file_gen = file_item
            self.return_values[file_path] = var_value
            self.unblocked_files.append(file_item)


def json_default(obj):
    if isinstance(obj, Interpolated):
        return str(obj)
    raise TypeError(repr(obj))


def unwrap_yielded(yielded):
    if isinstance(yielded, Block):
        yield dict(iter(yielded))
    elif isinstance(yielded, dict):
        yield yielded
    else:
        yield from yielded
