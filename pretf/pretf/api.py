import json
import os
import sys
from pathlib import Path

from . import log, util
from .render import Block, Renderer, json_default


def create(*source_dirs):
    """
    Creates *.tf.json and *.tfvars.json files in the current directory
    from *.tf.py and *.tfvars.py files in the source directories.

    Uses the current directory as a source directory if none are specified.
    If multiple directories are specified, and there are duplicate file names,
    the files in the latter directories take precedence.

    It is recommended to call create() only once. Pass in multiple
    source_dirs rather than calling it multiple times. Pretf parses
    variables from files in the current directory and the source_dirs.
    Calling it multiple times with different source_dirs could give
    Pretf a different set of files to parse each time it is called,
    resulting in different variables each time.

    """

    # Find all files in the specified source directories.
    files_to_create = {}
    for source_dir_path in map(Path, source_dirs or ["."]):
        for path in source_dir_path.iterdir():
            name = path.name
            if name.endswith(".tf.py") or name.endswith(".tfvars.py"):
                output_name = path.with_suffix(".json").name
                files_to_create[output_name] = path

    # Render the JSON data from *.tf.py and *.tfvars.py files.
    file_renderer = Renderer(files_to_create)
    file_contents = file_renderer.render()

    # Write JSON files.
    created = []
    for output_path, contents in sorted(file_contents.items()):
        with output_path.open("w") as open_file:
            json.dump(contents, open_file, indent=2, default=json_default)
        log.ok(f"create: {output_path.name}")
        created.append(output_path)

    return created


def execute(verbose=True):
    """
    Executes Terraform and waits for it to finish.
    Command line arguments are passed through to Terraform.
    Returns the exit code from Terraform.

    """

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
        return util.execute(
            file=terraform_path, args=["terraform"] + sys.argv[1:], verbose=verbose
        )

    log.bad("terraform: command not found")
    return 1


def mirror(*path_patterns, exclude_name_patterns=[".*", "_*"], cwd=None, verbose=True):
    """
    Creates symlinks from all files and directories matching
    the source patterns into the current directory. Deletes
    all pre-existing symlinks in the current directory.

    """

    if cwd is None:
        cwd = Path.cwd()

    if verbose:
        log.ok(f"mirror: {' '.join(path_patterns)}")

    # Delete old symlinks.
    for path in cwd.iterdir():
        if path.is_symlink():
            path.unlink()

    # Create new symlinks.
    created = []
    paths = util.find_paths(path_patterns, exclude_name_patterns=exclude_name_patterns)
    for real_path in paths:
        link_path = cwd / real_path.name
        link_path.symlink_to(real_path)
        created.append(link_path)

    return created


def remove(exclude=None):
    """
    Deletes all *.tf.json and *.tfvars.json files in the current directory.
    Optionally exclude specific files from being deleted.

    """

    removed = []

    old_paths = set()
    old_paths.update(Path().glob("*.tf.json"))
    old_paths.update(Path().glob("*.tfvars.json"))

    if isinstance(exclude, str):
        exclude = [exclude]

    if exclude:
        for path in exclude:
            old_paths.discard(path)

    for path in old_paths:
        path.unlink()
        removed.append(path)

    return removed


tf = Block

__all__ = ["create", "execute", "log", "mirror", "remove", "tf"]
