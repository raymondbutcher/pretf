import importlib
import json
import os
import pkgutil
import sys

from argparse import Namespace
from deepmerge import merge_or_raise
from functools import wraps
from glob import glob


__files__ = {}


class tf:

    def __init__(self, name, data):
        self.__name = name
        self.__data = data

    def __iter__(self):
        result = {}
        here = result
        for part in self.__name.split('.'):
            here[part] = {}
            here = here[part]
        here.update(self.__data)
        return iter(result.items())

    def __getattr__(self, attr):

        parts = self.__name.split('.')

        if parts[0] == 'resource':
            parts.pop(0)
        elif parts[0] == 'variable':
            parts[0] = 'var'

        parts.append(attr)

        return '${' + '.'.join(parts) + '}'

    def __str__(self):
        return self.__name


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


def _render(func, **kwargs):
    contents = {}
    for block in _blocks(func, **kwargs):
        contents = merge_or_raise.merge(
            contents,
            dict(iter(block)),
        )
    return contents


def create(*paths, **kwargs):
    result = []
    for path in paths:
        sys.path.insert(0, path)
        try:
            modules = pkgutil.iter_modules(path=[path])
            for module_finder, name, ispkg in modules:
                module = importlib.import_module(name)
                for name in dir(module):
                    func = getattr(module, name)
                    if callable(func):
                        if func in __files__:
                            result.append(func(**kwargs))
        finally:
            sys.path.pop(0)
    return result


def creates(path):

    def decorator(func):

        @wraps(func)
        def wrapped(**kwargs):
            contents = _render(func, **kwargs)
            with open(path, 'w') as open_file:
                json.dump(contents, open_file, indent=2)
            print(f'{path} written')
            return path

        __files__[wrapped] = path

        return wrapped

    return decorator


def remove(pattern, exclude=None):

    old_paths = set(glob(pattern))

    if isinstance(exclude, str):
        exclude = [exclude]
    
    if exclude:
        for path in exclude:
            old_paths.discard(path)

    for path in old_paths:
        print(f'{path} removed')
        os.remove(path)



