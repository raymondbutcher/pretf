import json
import os
import sys
from glob import glob
from pathlib import Path

from . import log, util
from .render import Renderer


def create():
    """
    Creates *.tf.json and *.tfvars.json files
    from *.tf.py and *.tfvars.py files.

    """

    # Render the JSON data from *.tf.py and *.tfvars.py files.
    file_contents = Renderer().render()

    # Write JSON files.
    created = []
    for file_path, contents in sorted(file_contents.items()):
        if contents:

            output_name = file_path.name[:-2] + "json"

            # Merge list of blocks into single block
            # in tfvars.json files.
            if output_name.endswith(".tfvars.json"):
                merged = {}
                for block in contents:
                    for name, value in block.items():
                        merged[name] = value
                contents = merged

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
    old_paths.update(glob("*.tfvars.json"))

    if isinstance(exclude, str):
        exclude = [exclude]

    if exclude:
        for path in exclude:
            old_paths.discard(path)

    for path in old_paths:
        os.remove(path)
        removed.append(path)

    return removed
