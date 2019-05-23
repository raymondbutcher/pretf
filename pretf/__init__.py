import importlib
import json
import pkgutil
import sys

from argparse import Namespace

from collections import defaultdict

from deepmerge import merge_or_raise

from functools import wraps


__files__ = {}


class tf:

    def __init__(self, name, data):
        self.__dict__['name'] = name
        self.__dict__['data'] = data

    def __iter__(self):
        result = {}
        here = result
        for part in self.__dict__['name'].split('.'):
            here[part] = {}
            here = here[part]
        here.update(self.__dict__['data'])
        return iter(result.items())

    def __getattr__(self, attr):
        return '${' + self.__dict__['name'] + '.' + attr + '}'

    def __str__(self):
        return self.__dict__['name']


def register_file(name):

    def decorator(func):

        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        __files__[wrapped] = name

        return wrapped

    return decorator


def _find_files(paths):
    for path in paths:
        sys.path.insert(0, path)
        try:
            for module_finder, name, ispkg in pkgutil.iter_modules(path=[path]):
                module = importlib.import_module(name)
                for name in dir(module):
                    func = getattr(module, name)
                    if callable(func):
                        file_name = __files__.get(func)
                        if file_name:
                            yield (file_name, path, func)
        finally:
            sys.path.pop(0)


def _get_blocks(func, params):
    gen = func(params)
    block = next(gen)
    yield block
    while True:
        try:
            yield gen.send(block)
        except StopIteration:
            break


def create_files(*paths, **params):
    # convert params into a dictattr thing
    # import python modules from paths
    # find any functions that have been registered
    # call functions and pass in params
    # write files

    files = defaultdict(dict)

    params = Namespace(**params)

    for file_name, source, func in _find_files(paths):
        for block in _get_blocks(func, params):
            print(f'{file_name}: {block}')
            files[file_name] = merge_or_raise.merge(
                files[file_name],
                dict(iter(block)),
            )

    for file_name, data in files.items():
        with open(file_name, 'w') as open_file:
            json.dump(data, open_file, indent=2)
        print(f'{file_name} written')


def run_terraform():
    pass
