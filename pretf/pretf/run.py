import json
import os
import sys
from collections import defaultdict
from glob import glob
from pathlib import Path

from . import log, util
from .render import Renderer


def create(*_paths, **_kwargs):
    """
    Creates *.tf.json files from *.tf.py files in the specified paths.
    Keyword arguments are passed along to the *.tf.py functions.

    """

    # Render the JSON data from *.tf.py files.
    file_contents = defaultdict(list)
    for file_name, block in Renderer(_paths, _kwargs).render():
        file_contents[file_name].append(block)

    # Write JSON files.
    created = []
    for file_name, contents in sorted(file_contents.items()):
        if contents:
            output_name = file_name[:-2] + "json"
            with open(output_name, "w") as open_file:
                json.dump(contents, open_file, indent=2)
            log.ok(f"create: {output_name}")
            created.append(output_name)

    return created


def execute(verbose=True):
    """
    Executes Terraform and waits for it to finish.
    Command line arguments are passed through to Terraform.
    Returns the exit code from Terraform.

    """

    return util.execute(
        file="terraform", args=["terraform"] + sys.argv[1:], verbose=verbose
    )


def mirror(*sources, target=".", exclude=["__pycache__"]):
    """
    Creates symlinks from all files and directories in the source
    directories into the target directory. Deletes all existing
    symlinks in the target directory.

    """

    target_path = Path(target)

    # Delete old symlinks in target path.
    for target_file_path in target_path.iterdir():
        if target_file_path.is_symlink():
            target_file_path.unlink()

    # Create new symlinks from source paths.
    for source in sources:
        if target == ".":
            log.ok(f"mirror: {source}")
        else:
            log.ok(f"mirror: {source} to {target}")
        source_path = Path(source)
        for source_file_path in source_path.iterdir():
            if source_file_path.name not in exclude:
                target_file_path = target_path / source_file_path.name
                target_file_path.symlink_to(source_file_path)


def remove(exclude=None):
    """
    Deletes all *.tf.json files in the current directory.
    Optionally exclude specific files from being deleted.

    """

    removed = []

    old_paths = set()
    old_paths.update(glob("*.tf.json"))

    if isinstance(exclude, str):
        exclude = [exclude]

    if exclude:
        for path in exclude:
            old_paths.discard(path)

    for path in old_paths:
        os.remove(path)
        removed.append(path)

    return removed
