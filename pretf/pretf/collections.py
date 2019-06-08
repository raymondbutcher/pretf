from functools import wraps

from .parser import get_outputs_from_block, get_variables_from_block
from .render import Block, VariableNotDefined, VariableNotPopulated


class Collection:
    def __init__(self, blocks, outputs):
        self.__blocks = blocks
        self.__outputs = outputs

    def __getattr__(self, name):
        try:
            return self.__outputs[name]
        except KeyError:
            raise AttributeError(f"output not defined: {name}")

    def __iter__(self):
        return iter(self.__blocks)


class VariableProxy:
    def __init__(self, values):
        self._variables = set()
        self._defaults = {}
        self._values = values

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, key):

        if key not in self._variables:
            raise VariableNotDefined(key, "pretf.collections")

        if key in self._values:
            return self._values[key]

        if key in self._defaults:
            return self._defaults[key]

        raise VariableNotPopulated(key, "pretf.collections")


def collect(func):
    """
    This is a decorator used to create a Collection.
    Decorated functions should:

    * accept a single argument "var"
    * yield pretf.api.tf blocks
        * optionally including variable blocks to define inputs
        * optionally including output blocks to define outputs

    When using a collection, any required inputs defined by variable blocks
    must be passed in as keyword arguments. Any outputs defined by output
    blocks can be accessed as attributes of the collection.

    """

    @wraps(func)
    def wrapped(**kwargs):

        var = VariableProxy(kwargs)

        blocks = []
        outputs = {}

        gen = func(var)
        yielded = None
        while True:

            try:
                yielded = gen.send(yielded)
            except StopIteration:
                break

            if isinstance(yielded, Block):
                block = dict(iter(yielded))
            elif isinstance(yielded, dict):
                block = yielded
            else:
                raise TypeError(yielded)

            variable = None
            for variable in get_variables_from_block(block):
                name = variable["name"]
                var._variables.add(name)
                if "default" in variable:
                    var._defaults[name] = variable["default"]

            output = None
            for output in get_outputs_from_block(block):
                name = output["name"]
                value = output["value"]
                outputs[name] = value

            if not variable and not output:
                blocks.append(block)

        return Collection(blocks, outputs)

    return wrapped
