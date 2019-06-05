import os

from .util import import_file


class Block:
    def __init__(self, path, body):
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
        return iter(result.items())

    def __getattr__(self, attr):

        parts = self.__path.split(".")

        if parts[0] == "resource":
            parts.pop(0)
        elif parts[0] == "variable":
            parts[0] = "var"

        parts.append(attr)

        return "${" + ".".join(parts) + "}"

    def __repr__(self):
        return f"Block({self})"

    def __str__(self):
        return self.__path


class Renderer:
    def __init__(self, paths, kwargs):
        self.paths = paths or ["."]
        self.kwargs = kwargs

    def render(self):

        files = []

        # Check for files.
        for path in self.paths:
            for name in os.listdir(path):
                if name.endswith(".tf.py"):
                    # Add to list of files to generate.
                    with import_file(name) as module:
                        file_gen = module.terraform(**self.kwargs)
                    file_item = [name, file_gen]
                    files.append(file_item)

        # Generate *.tf.json files from *.tf.py files.
        send_queue = {}
        while files:

            file_item = files.pop()
            file_name, file_gen = file_item

            try:
                if file_name in send_queue:
                    yielded = file_gen.send(send_queue.pop(file_name))
                else:
                    yielded = next(file_gen)
            except StopIteration:
                continue

            # The file generator yielded a Block (or a raw dictionary,
            # or an invalid value). Add it to the file contents to be
            # written as JSON.

            if isinstance(yielded, Block):
                # Convert the block into a dictionary.
                block = dict(iter(yielded))
            elif isinstance(yielded, dict):
                block = yielded
            else:
                raise TypeError(f"{yielded} in {file_name}")

            # Yield the block so it can be included in the rendered file.
            yield (file_name, block)

            send_queue[file_name] = yielded
            files.append(file_item)
