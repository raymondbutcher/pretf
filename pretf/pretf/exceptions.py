from collections import defaultdict
from os.path import relpath
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Sequence

if TYPE_CHECKING:
    from pretf.variables import VariableDefinition, VariableValue  # noqa: F401


class FunctionNotFoundError(Exception):
    pass


class RequiredFilesNotFoundError(Exception):
    def __init__(self, name_patterns: Sequence[str], root: Path):
        self.name_patterns = name_patterns
        self.root = root

    def get_candidates(self) -> List[str]:

        dirs: Dict[Path, List[str]] = defaultdict(list)
        for pattern in self.name_patterns:
            for path in self.root.rglob(pattern):
                dirs[path.parent].append(pattern)

        matching_dirs = []
        for path, patterns in dirs.items():
            if len(patterns) == len(self.name_patterns):
                matching_dirs.append(path)

        relative_paths = []
        for path in sorted(matching_dirs):
            relative_paths.append(relpath(path))

        return relative_paths


class VariableError(Exception):
    def __init__(self) -> None:
        self.errors: List[VariableError] = []

    def add(self, error: "VariableError") -> None:
        self.errors.append(error)

    def __str__(self) -> str:
        errors = "\n".join(f"  {error}" for error in self.errors)
        return f"\n{errors}"


class VariableAlreadyDefinedError(VariableError):
    def __init__(
        self, old_var: "VariableDefinition", new_var: "VariableDefinition"
    ) -> None:
        self.old_var = old_var
        self.new_var = new_var

    def __str__(self) -> str:
        return f"create: {self.new_var.source} cannot define var.{self.new_var.name} because {self.old_var.source} already defined it"


class VariableNotConsistentError(VariableError):
    def __init__(self, old_var: "VariableValue", new_var: "VariableValue") -> None:
        self.old_var = old_var
        self.new_var = new_var

    def __str__(self) -> str:
        return f"create: {self.new_var.source} cannot set var.{self.new_var.name}={repr(self.new_var.value)} because {self.old_var.source} set var.{self.old_var.name}={repr(self.old_var.value)}"


class VariableNotDefinedError(VariableError):
    def __init__(self, name: str, consumer: str):
        self.name = name
        self.consumer = consumer

    def __str__(self) -> str:
        return f"create: {self.consumer} cannot access var.{self.name} because it has not been defined"


class VariableNotPopulatedError(VariableError):
    def __init__(self, name: str, consumer: str):
        self.name = name
        self.consumer = consumer

    def __str__(self) -> str:
        return f"create: {self.consumer} cannot access var.{self.name} because it has no value"
