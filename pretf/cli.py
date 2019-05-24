import json
import os
import sys

from argparse import Namespace
from deepmerge import merge_or_raise
from glob import glob

from . import __version__, log, terraform


def _create(*paths, **kwargs):
    result = []
    for name, main in _load(paths):

        # Render the Terraform blocks.
        contents = _render(main, **kwargs)

        # Write JSON file.
        output_name = f"{name}.tf.json"
        with open(output_name, "w") as open_file:
            json.dump(contents, open_file, indent=2)

        log.ok(f"create: {output_name}")
        result.append(output_name)

    return result


def _blocks(func, **kwargs):
    params = Namespace(**kwargs)
    gen = func(params)
    block = next(gen)
    yield block
    while True:
        try:
            block = gen.send(block)
            yield block
        except StopIteration:
            break


def _load(paths):
    for path in paths:
        sys.path.insert(0, path)
        try:
            for name in os.listdir(path):
                if name.endswith(".tf.py"):
                    global_scope = {}
                    with open(os.path.join(path, name)) as open_file:
                        exec(open_file.read(), global_scope)
                    yield (name[:-6], global_scope["main"])
        finally:
            sys.path.pop(0)
    return []


def _remove(*patterns, exclude=None):

    old_paths = set()
    for pattern in patterns:
        old_paths.update(glob(pattern))

    if isinstance(exclude, str):
        exclude = [exclude]

    if exclude:
        for path in exclude:
            old_paths.discard(path)

    for path in old_paths:
        log.ok(f"remove: {path}")
        os.remove(path)


def _render(func, **kwargs):
    contents = {}
    for block in _blocks(func, **kwargs):
        contents = merge_or_raise.merge(contents, dict(iter(block)))
    return contents


def run():

    # Version command.
    args = sys.argv[1:]
    cmd = args[0] if args else None
    if cmd in ("version", "-v", "-version", "--version"):
        print(f"Pretf v{__version__}")
        terraform.execute()
        return

    # Read configuration file.
    with open("pretf.json") as open_file:
        config = json.load(open_file)

    # Write files.
    value = config.get("source")
    if value:
        if isinstance(value, str):
            source_paths = [value]
        else:
            source_paths = value
    else:
        source_paths = ["."]
    params = config.get("params") or {}
    created = _create(*source_paths, **params)

    # Remove old files.
    value = config.get("remove")
    if value:
        if isinstance(value, str):
            remove_paths = [value]
        else:
            remove_paths = value
        _remove(*remove_paths, exclude=created)

    # Run Terraform.
    log.ok("run: terraform")
    terraform.execute()
