import json
import sys
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

            output_path = file_path.with_suffix(".json")

            # Merge list of blocks into single block
            # in tfvars.json files.
            if output_path.name.endswith(".tfvars.json"):
                merged = {}
                for block in contents:
                    for name, value in block.items():
                        merged[name] = value
                contents = merged

            with output_path.open("w") as open_file:
                json.dump(contents, open_file, indent=2)

            log.ok(f"create: {output_path.name}")
            created.append(output_path)

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

    created = []

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
                created.append(target_file_path)

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
