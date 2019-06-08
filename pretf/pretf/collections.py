from functools import wraps

from .parser import get_outputs_from_block, get_variables_from_block
from .render import Collection, unwrap_yielded
from .variables import VariableNotDefined, VariableNotPopulated


class VariableProxy:
    def __init__(self, values):
        self._defaults = {}
        self._names = set()
        self._values = values

    def __getattr__(self, name):

        if name not in self._names:
            raise VariableNotDefined(name, "pretf.collections")

        if name in self._values:
            return self._values[name]

        if name in self._defaults:
            return self._defaults[name]

        raise VariableNotPopulated(name, "pretf.collections")

    __getitem__ = __getattr__


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

        var_proxy = VariableProxy(kwargs)
        gen = func(var_proxy)

        blocks = []
        outputs = {}

        yielded = None
        while True:

            try:
                yielded = gen.send(yielded)
            except StopIteration:
                break

            for block in unwrap_yielded(yielded):

                var = None
                for var in get_variables_from_block(block):
                    name = var["name"]
                    var_proxy._names.add(name)
                    if "default" in var:
                        var_proxy._defaults[name] = var["default"]

                output = None
                for output in get_outputs_from_block(block):
                    name = output["name"]
                    value = output["value"]
                    outputs[name] = value

                if not var and not output:
                    blocks.append(block)

        return Collection(blocks, outputs)

    return wrapped
