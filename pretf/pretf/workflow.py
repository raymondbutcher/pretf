import inspect
import json
import os
import shlex
import sys
from pathlib import Path, PurePath
from subprocess import CalledProcessError, CompletedProcess
from typing import Any, Dict, List, Optional, Sequence, Union

from . import log, util
from .exceptions import RequiredFilesNotFoundError
from .render import call_pretf_function, json_default, render_files
from .util import import_file, is_verbose


def clean_files(paths: Sequence[Path], verbose: Optional[bool] = None) -> None:
    """
    Deletes the specified files. Intended for use after `create_files()`.
    Use `delete_files()` if wildcards are required.

    """

    if paths and is_verbose(verbose):
        names = [path.name for path in paths]
        log.ok(f"clean: {' '.join(sorted(names))}")

    for path in paths:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def create_files(
    target_dir: Union[Path, str] = "",
    source_dirs: Sequence[Union[Path, str]] = [],
    verbose: Optional[bool] = None,
) -> List[Path]:
    """
    Creates *.tf.json and *.tfvars.json files in target_dir
    from *.tf.py and *.tfvars.py in source_dirs.

    Both target_dir and source_dirs will default to the directory
    specified in the CLI arguments, if specified, otherwise the current
    working directory.

    If multiple source_dirs are specified, and there are duplicate
    file names, the files in the latter directories take precedence.

    It is recommended to call create() only once. Pass in multiple
    source_dirs rather than calling it multiple times. Pretf parses
    variables from files in the current directory and the source_dirs.
    Calling it multiple times with different source_dirs could give
    Pretf a different set of files to parse each time it is called,
    resulting in different variables each time.

    """

    if not target_dir:
        _, _, _, config_dir = util.parse_args()
        target_dir = config_dir

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
        file_contents = render_files(files_to_create)
    else:
        file_contents = {}

    if file_contents and is_verbose(verbose):
        names = [path.name for path in file_contents.keys()]
        log.ok(f"create: {' '.join(sorted(names))}")

    # Write JSON files.
    created = []
    for output_path, contents in sorted(file_contents.items()):
        with output_path.open("w") as open_file:
            json.dump(contents, open_file, indent=2, default=json_default)
        created.append(output_path)

    return created


def custom(
    path: Union[PurePath, str], context: Optional[dict] = None
) -> CompletedProcess:
    """
    Calls the pretf_workflow() function from the specified Python file.
    This is useful for having a custom workflow that is used by multiple
    pretf.workflow.py files in different directories.

    """

    with import_file(path) as module:

        if not hasattr(module, "pretf_workflow"):
            raise log.bad(f"workflow: {path} does not have a 'pretf_workflow' function")

        # Call the pretf_workflow() function,
        # passing in "path" and "terraform" if required.
        result = call_pretf_function(func=module.pretf_workflow, context=context)  # type: ignore

    if isinstance(result, int):
        result = CompletedProcess(args=[str(path)], returncode=result)

    return result


def default(
    clean: bool = True, created: list = [], verbose: Optional[bool] = None
) -> CompletedProcess:
    """
    This is the default Pretf workflow. This is automatically used when there
    is no pretf.workflow.py file in the current directory, or it can be called
    directly from a custom workflow function if it just needs to do something
    before or after the default workflow.

    """

    # Delete *.tf.json and *.tfvars.json files.
    delete_files(verbose=verbose)

    # Create *.tf.json and *.tfvars.json files
    # from *.tf.py and *.tfvars.py files.
    created = created + create_files(verbose=verbose)

    # Execute Terraform, raising an exception if it fails.
    proc = execute_terraform(verbose=verbose)

    # Clean up created files.
    if clean:
        clean_files(paths=created, verbose=verbose)

    return proc


def delete_files(
    *path_patterns: str,
    exclude_name_patterns: Sequence[str] = [],
    cwd: Optional[Union[Path, str]] = None,
    verbose: Optional[bool] = None,
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

    # Find files to delete.
    delete = []
    paths = util.find_paths(
        path_patterns=path_patterns,
        exclude_name_patterns=exclude_name_patterns,
        cwd=cwd,
    )
    for path in paths:
        if not path.is_dir():
            delete.append(path)

    if delete and is_verbose(verbose):
        names = [path.name for path in delete]
        log.ok(f"delete: {' '.join(sorted(names))}")

    # Delete files.
    deleted = []
    for path in delete:
        path.unlink()
        deleted.append(path)

    return deleted


def delete_links(
    cwd: Optional[Union[Path, str]] = None, verbose: Optional[bool] = None
) -> List[Path]:
    """
    Deletes symlinks from the current directory.

    """

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    # Find links to delete.
    delete = []
    for path in cwd.iterdir():
        if path.is_symlink():
            delete.append(path)

    if delete and is_verbose(verbose):
        names = [path.name for path in delete]
        log.ok(f"unlink: {' '.join(sorted(names))}")

    # Delete links.
    deleted = []
    for path in delete:
        path.unlink()
        deleted.append(path)

    return deleted


def execute_terraform(
    args: Optional[Sequence[str]] = None,
    cwd: Optional[Union[Path, str]] = None,
    env: Optional[dict] = None,
    capture: bool = False,
    verbose: Optional[bool] = None,
) -> CompletedProcess:
    """
    Executes Terraform and waits for it to finish.
    Command line arguments are passed through to Terraform.
    Returns the exit code from Terraform.

    """

    if args is None:
        args = ["terraform"] + sys.argv[1:]
    else:
        args = ["teraform"] + list(args)

    # Find the Terraform executable in the PATH.
    for path in os.environ["PATH"].split(os.pathsep):

        if sys.platform == "win32":
            terraform_path = os.path.join(path, "terraform.exe")
        else:
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
        return util.execute(
            file=terraform_path, args=args, cwd=cwd, capture=capture, verbose=verbose
        )

    log.bad("terraform: command not found")
    raise CalledProcessError(
        returncode=1, cmd=" ".join(shlex.quote(arg) for arg in args),
    )


def load_parent(**kwargs: Any) -> CompletedProcess:
    """
    Looks for the closest pretf.workflow.py file in parent directories
    and calls the pretf_workflow() function. Errors if there are no
    pretf.workflow.py files in any parent directories.

    """

    # Find the calling directory of this function, usually the directory
    # containing the pretf.workflow.py file that has called this function.
    frame = inspect.currentframe()
    if not frame:
        raise Exception("workflow: load_parent() called from unknown frame")
    caller_frame = frame.f_back
    if not caller_frame:
        raise Exception("workflow: load_parent() called from unknown caller")
    caller_info = inspect.getframeinfo(caller_frame)
    caller_file = caller_info.filename
    caller_directory = Path(caller_file).parent

    # Look for pretf.workflow.py in parent directories.
    parent_directory = caller_directory.parent
    path = util.find_workflow_path(cwd=parent_directory)

    if not path:
        raise log.bad(
            f"workflow: load_parent() called in {caller_file} but pretf.workflow.py not found in parent directories"
        )

    return custom(path, context=kwargs)


def link_files(
    *path_patterns: Union[Path, str],
    exclude_name_patterns: Sequence[str] = [".*", "_*", "pretf.workflow.py"],
    cwd: Optional[Union[Path, str]] = None,
    verbose: Optional[bool] = None,
) -> List[Path]:
    """
    Creates symlinks from all files and directories matching
    the source patterns into the current directory.

    """

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    # Find the calling directory of this function, usually the directory
    # containing the pretf.workflow.py file that has called this function.
    frame = inspect.currentframe()
    if not frame:
        raise Exception("workflow: link_files() called from unknown frame")
    caller_frame = frame.f_back
    if not caller_frame:
        raise Exception("workflow: link_files() called from unknown caller")
    caller_info = inspect.getframeinfo(caller_frame)
    caller_file = caller_info.filename
    caller_directory = Path(caller_file).parent

    # Start a list of source paths to symlink into the working directory.
    paths: List[Path] = []

    # Separate the path patterns into file name patterns (no slashes)
    # and ones that represent relative paths (can be absolute too).
    name_patterns: List[str] = []
    relative_patterns: List[str] = []
    for value in path_patterns:
        if isinstance(value, Path):
            # Use Path objects directly.
            paths.append(value)
        elif isinstance(value, str):
            if "/" in value:
                relative_patterns.append(value)
            else:
                name_patterns.append(value)
        else:
            raise TypeError(value)

    # Find paths relative to the working directory (can be absolute too).
    if relative_patterns:
        paths.extend(
            util.find_paths(
                path_patterns=relative_patterns,
                exclude_name_patterns=exclude_name_patterns,
                cwd=cwd,
            )
        )

    # Find files in parent directories of the working directory up to
    # the directory with the pretf.workflow.py file that called this.
    if name_patterns:
        here = cwd.parent
        while True:
            try:
                here.relative_to(caller_directory)
            except ValueError:
                break
            else:
                paths.extend(
                    util.find_paths(
                        path_patterns=name_patterns,
                        exclude_name_patterns=exclude_name_patterns,
                        cwd=here,
                    )
                )
                here = here.parent

    # Create a map of symlink paths to original paths.
    create: Dict[Path, str] = {}
    for real_path in paths:

        try:
            cwd.relative_to(os.path.normpath(real_path))
        except ValueError:
            is_parent_directory = False
        else:
            is_parent_directory = True

        if is_parent_directory:
            continue

        link_path = cwd / real_path.name

        if link_path in create:
            continue

        if link_path.exists():
            continue

        relative_path = os.path.relpath(real_path, cwd)

        create[link_path] = relative_path

    if create and is_verbose(verbose):
        names = [path.name for path in create.keys()]
        log.ok(f"link: {' '.join(sorted(names))}")

    # Create new symlinks.
    created = []
    for link_path, relative_path in create.items():
        link_path.symlink_to(relative_path)
        created.append(link_path)

    return created


def link_module(
    source: str,
    version: Optional[str] = None,
    update: bool = False,
    cache_dir: Optional[Union[Path, str]] = None,
    cwd: Optional[Union[Path, str]] = None,
    verbose: Optional[bool] = None,
) -> List[Path]:
    """
    Creates symlinks from all files and directories in a module into
    the current directory. Remote modules are first downloaded into a
    cache directory.

    """

    if is_verbose(verbose):
        if version:
            log.ok(f"module: {source} {version}")
        else:
            log.ok(f"module: {source}")

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    paths: List[Path] = []

    if source.startswith(".") or source.startswith("/"):

        # Modules already on the filesystem can be used directly.
        paths.extend(util.find_paths(path_patterns=["*"], cwd=source,))

    else:

        # Remote modules will be managed by Terraform in a
        # cache directory and then symlinked from there.
        module_name = "mirror-module"

        # Ensure the module cache directory exists.
        if cache_dir is None:
            cache_dir = cwd / ".terraform" / "pretf" / module_name
        elif isinstance(cache_dir, str):
            cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Create a Terraform root module in the cache directory
        # that just references the specified module.
        module_config_path = cache_dir / "main.tf.json"
        module_body = {"source": source}
        if version:
            module_body["version"] = version
        module_json = json.dumps([{"module": {module_name: module_body}}], indent=2)
        module_config_path.write_text(module_json)

        # Run "terraform get" to download the module using Terraform.
        from .test import TerraformProxy

        terraform_get_args = ["-update"] if update else []
        TerraformProxy(cwd=cache_dir).get(*terraform_get_args)

        # Get the path to the module.
        modules_manifest_path = cache_dir / ".terraform" / "modules" / "modules.json"
        modules_manifest = json.loads(modules_manifest_path.read_text())
        for module in modules_manifest["Modules"]:
            if module["Key"] == module_name:
                module_dir = cache_dir / module["Dir"]
                # Use files from the downloaded module directory.
                paths.extend(util.find_paths(path_patterns=["*"], cwd=module_dir))

    return link_files(*paths, cwd=cwd, verbose=verbose)


def mirror_files(
    *path_patterns: str,
    exclude_name_patterns: Sequence[str] = [".*", "_*"],
    include_directories: bool = True,
    cwd: Optional[Union[Path, str]] = None,
    verbose: Optional[bool] = None,
) -> List[Path]:
    """
    Creates symlinks from all files and directories matching
    the source patterns into the current directory. Deletes
    all pre-existing symlinks in the current directory.
    """

    log.bad("workflow: mirror_files() has been deprecated")

    if cwd is None:
        cwd = Path.cwd()
    elif isinstance(cwd, str):
        cwd = Path(cwd)

    # Delete old symlinks.
    for path in cwd.iterdir():
        if path.is_symlink():
            if not include_directories and path.is_dir():
                continue
            path.unlink()

    # Find files to mirror.
    create = {}
    paths = util.find_paths(
        path_patterns=path_patterns,
        exclude_name_patterns=exclude_name_patterns,
        cwd=cwd,
    )
    for real_path in paths:

        try:
            cwd.relative_to(os.path.normpath(real_path))
        except ValueError:
            is_parent_directory = False
        else:
            is_parent_directory = True

        if is_parent_directory:
            continue

        if not include_directories and real_path.is_dir():
            continue

        link_path = cwd / real_path.name

        if link_path.exists():
            continue

        relative_path = os.path.relpath(real_path, cwd)

        create[link_path] = relative_path

    if create and is_verbose(verbose):
        names = [path.name for path in create.keys()]
        log.ok(f"mirror: {' '.join(sorted(names))}")

    # Create new symlinks.
    created = []
    for link_path, relative_path in create.items():
        link_path.symlink_to(relative_path)
        created.append(link_path)

    return created


def require_files(*name_patterns: str) -> None:
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

    # Find the calling directory of this function, usually the directory
    # containing the pretf.workflow.py file that has called this function.
    frame = inspect.currentframe()
    if not frame:
        raise Exception("workflow: require_files() called from unknown frame")
    caller_frame = frame.f_back
    if not caller_frame:
        raise Exception("workflow: require_files() called from unknown caller")
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
