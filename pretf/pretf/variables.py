import os
import shlex
import sys
from pathlib import Path

from .parser import get_variables_from_file_with_source


class TerraformVariables:
    def __init__(self, file_paths):
        self._cli_var_files = set()
        self._defaults = {}
        self._file_paths = file_paths
        self._file_paths_preventing_defaults = set()
        self._loaded = False
        self._loading = False
        self._names = set()
        self._sources = {}
        self._values = {}

    def _load(self):
        if not self._loaded:
            if not self._loading:
                self._loading = True
                for var in self._load_terraform_variables():
                    self.add(var)
                self._loading = False
                self._loaded = True

    def _load_terraform_variables(self):
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

        file_paths_groups = {"auto": [], "vars": [], "default": []}
        suffix_groups = {
            ".auto.tfvars.json": "auto",
            ".auto.tfvars": "auto",
            ".tf.json": "vars",
            ".tf": "vars",
        }

        for file_path in sorted(self._file_paths):
            if file_path.name in ("terraform.tfvars", "terraform.tfvars.json"):
                file_paths_groups["default"].append(file_path)
            else:
                for suffix, group in suffix_groups.items():
                    if file_path.name.endswith(suffix):
                        file_paths_groups[group].append(file_path)

        # Load variable definitions.
        for file_path in file_paths_groups["vars"]:
            yield from get_variables_from_file_with_source(file_path)

        # Load variable values.
        # 1. Environment variables.
        for key, value in os.environ.items():
            if key.startswith("TF_VAR_"):
                name = key[7:]
                yield {"name": name, "value": value, "source": key}

        # 2. The terraform.tfvars file, if present.
        # 3. The terraform.tfvars.json file, if present.
        for file_path in file_paths_groups["default"]:
            yield from get_variables_from_file_with_source(file_path)

        # 4. Any *.auto.tfvars or *.auto.tfvars.json files,
        #    processed in lexical order of their filenames.
        for file_path in file_paths_groups["auto"]:
            yield from get_variables_from_file_with_source(file_path)

        # 5. Any -var and -var-file options on the command line,
        #    in the order they are provided.
        for arg in sys.argv[1:]:
            if arg.startswith("-var="):
                var_string = shlex.split(arg[5:])[0]
                name, value = var_string.split("=", 1)
                yield {"name": name, "value": value, "source": arg}
            elif arg.startswith("-var-file="):
                file_path = Path(os.path.abspath(arg[10:]))
                if file_path in self._file_paths or file_path.exists():
                    yield from get_variables_from_file_with_source(file_path)
                else:
                    self._cli_var_files.add(file_path)

    def add(self, var):
        """
        Adds a variable. Returns True if it was a new value.

        """

        self._load()

        name = var["name"]
        source = var["source"]

        if "value" in var:

            value = var["value"]

            if not self._loading:
                if name in self.__values and self.__values[name] != value:
                    old_source = self.get_source(name)
                    raise VariableNotConsistent(
                        name, old_source=old_source, new_source=source
                    )

            self._values[name] = value
            self._sources[name] = source

        else:

            self._names.add(name)

            if "default" in var:

                self._defaults[name] = var["default"]
                self._sources.setdefault(name, source)

    def disable_defaults(self, file_path):
        self._file_paths_preventing_defaults.add(file_path)

    def enable_defaults(self, file_path):
        self._file_paths_preventing_defaults.remove(file_path)

    def get_value(self, name, path):

        self._load()

        if name not in self._names:
            raise VariableNotDefined(name, path)

        if name in self._values:
            return self._values[name]

        if not self._file_paths_preventing_defaults:
            if name in self._defaults:
                return self._defaults[name]

        raise VariableNotPopulated(name, path)

    def get_source(self, name):
        return self._sources[name]

    def is_source_file(self, file_path):

        name = file_path.name

        if name == "terraform.tfvars.py":
            return True

        if name.endswith(".auto.tfvars.py"):
            return True

        output_file_path = file_path.with_suffix(".json")
        if output_file_path in self._cli_var_files:
            return True

        return False


class VariableError(Exception):
    def __init__(self):
        self.errors = []

    def add(self, error):
        self.errors.append(error)

    def __str__(self):
        errors = "\n".join(f"  {error}" for error in self.errors)
        return f"\n{errors}"


class VariableNotConsistent(VariableError):
    def __init__(self, name, old_source, new_source):
        self.name = name
        self.old_source = old_source
        self.new_source = new_source

    def __str__(self):
        return f"create: {self.new_source} cannot set value for var.{self.name} because {self.old_source} set it with a different value"


class VariableNotDefined(VariableError):
    def __init__(self, name, source):
        self.name = name
        self.source = source

    def __str__(self):
        return f"create: {self.source} cannot access var.{self.name} because it has not been defined"


class VariableNotPopulated(VariableError):
    def __init__(self, name, source):
        self.name = name
        self.source = source

    def __str__(self):
        return f"create: {self.source} cannot access var.{self.name} because it has no value"
