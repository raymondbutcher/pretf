import inspect
import json
import os
import sys
from pathlib import Path, PurePath
from subprocess import CompletedProcess
from typing import List, Optional, Sequence, Union

from . import log, util
from .exceptions import FunctionNotFoundError, RequiredFilesNotFoundError
from .render import Renderer, call_pretf_function, json_default
from .util import import_file


def create_files(
    target_dir: Union[Path, str] = "",
    source_dirs: Sequence[Union[Path, str]] = [],
    verbose: bool = True,
) -> List[Path]:
    """
    Creates *.tf.json and *.tfvars.json files in target_dir
    from *.tf.py and *.tfvars.py in source_dirs.

    target_dir defaults to the current working directory and
    source_dirs defaults to a list containing target_dir.

    If multiple source_dirs are specified, and there are duplicate
    file names, the files in the latter directories take precedence.

    It is recommended to call create() only once. Pass in multiple
    source_dirs rather than calling it multiple times. Pretf parses
    variables from files in the current directory and the source_dirs.
    Calling it multiple times with different source_dirs could give
    Pretf a different set of files to parse each time it is called,
    resulting in different variables each time.

    """

    if isinstance(target_dir, str):
        target_dir = Path(target_dir)

    if not source_dirs:
        source_dirs = [target_dir]

    # Find all files in the specified source directories.
    files_to_create = {}
    for source_dir in source_dirs or ["."]:
        if isinstance(source_dir, str):
            source_dir = Path(source_dir)
        for source_path in source_dir.iterdir():
            file_name = source_path.name
            if file_name.endswith(".tf.py") or file_name.endswith(".tfvars.py"):
                target_path = (target_dir / file_name).with_suffix(".json")
                files_to_create[target_path] = source_path

    # Render the JSON data from *.tf.py and *.tfvars.py files.
    if files_to_create:
        file_contents = Renderer(files_to_create).render()
    else:
        file_contents = {}

    # Write JSON files.
    created = []
    for output_path, contents in sorted(file_contents.items()):
        with output_path.open("w") as open_file:
            json.dump(contents, open_file, indent=2, default=json_default)
        if verbose:
            log.ok(f"create: {output_path.name}")
        created.append(output_path)

    return created


def custom(path: Union[PurePath, str]) -> CompletedProcess:
    """
    Calls the pretf_workflow() function from the specified Python file.
    This is useful for having a custom workflow that is used by multiple
    pretf.py files in different directories.

    """

    with import_file(path) as module:

        if not hasattr(module, "pretf_workflow"):
            raise FunctionNotFoundError(
                f"workflow: {path} does not have a 'pretf_workflow' function"
            )

        # Call the pretf_workflow() function,
        # passing in "path" and "terraform" if required.
        result = call_pretf_function(func=module.pretf_workflow)  # type: ignore

    if not isinstance(result, CompletedProcess):

        result = CompletedProcess(args=[str(path)], returncode=1)

    return result


def default(verbose: bool = True) -> CompletedProcess:
    """
    This is the default Pretf workflow. This is automatically used when there
    is no pretf.py file in the current directory, or it can be called directly
    from a custom workflow function if it just needs to do something before
    or after the default workflow.

    """

    # Delete *.tf.json and *.tfvars.json files.
    delete_files(verbose=verbose)

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    create_files(verbose=verbose)

    # Execute Terraform.
    return execute_terraform(verbose=verbose)


def delete_files(
    *path_patterns: str,
    exclude_name_patterns: Sequence[str] = [],
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:
    """
    Deletes matching files from the current directory.
    Defaults to deleting files normally created by the create() function.
    Optionally exclude files matching a specified pattern.

    """

    if not path_patterns:
        path_patterns = ("*.tf.json", "*.tfvars.json")

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    if verbose:
        log.ok(f"remove: {' '.join(path_patterns)}")

    # Find files to delete.
    paths = util.find_paths(
        path_patterns=path_patterns,
        exclude_name_patterns=exclude_name_patterns,
        cwd=cwd,
    )

    # Delete files.
    deleted = []
    for path in paths:
        if not path.is_dir():
            path.unlink()
            deleted.append(path)

    return deleted


def execute_terraform(verbose: bool = True) -> CompletedProcess:
    """
    Executes Terraform and waits for it to finish.
    Command line arguments are passed through to Terraform.
    Returns the exit code from Terraform.

    """

    args = ["terraform"] + sys.argv[1:]

    # Find the Terraform executable in the PATH.
    for path in os.environ["PATH"].split(os.pathsep):

        terraform_path = os.path.join(path, "terraform")

        # Skip if it doesn't exist here.
        if not os.path.exists(terraform_path):
            continue

        # Skip if it's not executable.
        if not os.access(terraform_path, os.X_OK):
            continue

        # Skip if it's a symlink to Pretf.
        real_name = os.path.basename(os.path.realpath(terraform_path))
        if real_name == "pretf":
            continue

        # This is a valid executable, run it.
        return util.execute(file=terraform_path, args=args, verbose=verbose)

    log.bad("terraform: command not found")
    return CompletedProcess(args=args, returncode=1)


def mirror_files(
    *path_patterns: str,
    exclude_name_patterns: Sequence[str] = [".*", "_*"],
    include_directories: bool = True,
    cwd: Optional[Union[Path, str]] = None,
    verbose: bool = True,
) -> List[Path]:
    """
    Creates symlinks from all files and directories matching
    the source patterns into the current directory. Deletes
    all pre-existing symlinks in the current directory.

    """

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    if verbose:
        log.ok(f"mirror: {' '.join(path_patterns)}")

    # Find files to mirror.
    paths = util.find_paths(
        path_patterns=path_patterns,
        exclude_name_patterns=exclude_name_patterns,
        cwd=cwd,
    )

    # Delete old symlinks.
    for path in cwd.iterdir():
        if not include_directories and path.is_dir():
            continue
        if path.is_symlink():
            path.unlink()

    # Create new symlinks.
    created = []
    for real_path in paths:
        if not include_directories and real_path.is_dir():
            continue
        link_path = cwd / real_path.name
        if link_path.exists():
            continue
        link_path.symlink_to(real_path)
        created.append(link_path)

    return created


def require_files(*name_patterns: str, verbose: bool = True) -> None:
    """
    Raises an exception if the specified files are not found in the current
    directory. Pretf will catch this exception, display an error message,
    and show other directories that do contain the files.

    This can be used to restrict where Pretf/Terraform can run,
    while informing users where it can run if they make a mistake.

    If multiple patterns are provided, the directory must contain
    files that match all patterns (performing an AND search).

    """

    cwd = Path.cwd()

    matches = 0
    for pattern in name_patterns:
        if list(cwd.glob(pattern)):
            matches += 1

    if matches == len(name_patterns):
        return

    caller_frame = inspect.currentframe().f_back  # type: ignore
    caller_info = inspect.getframeinfo(caller_frame)
    caller_file = caller_info.filename
    caller_directory = Path(caller_file).parent

    raise RequiredFilesNotFoundError(name_patterns=name_patterns, root=caller_directory)


__all__ = [
    "create_files",
    "custom",
    "default",
    "delete_files",
    "execute_terraform",
    "mirror_files",
    "require_files",
]
