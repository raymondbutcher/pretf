from functools import wraps
from typing import Any, Callable, Generator, Iterable, Sequence, Union

from .parser import get_outputs_from_block
from .render import call_pretf_function, unwrap_yielded
from .variables import VariableStore, VariableValue, get_variable_definitions_from_block


class Collection(Iterable):
    def __init__(
        self, blocks: Sequence[Union[dict, "Collection"]], outputs: dict
    ) -> None:
        self.__blocks = blocks
        self.__outputs = outputs

    def __getattr__(self, name: str) -> Any:
        if name in self.__outputs:
            return self.__outputs[name]
        raise AttributeError(f"output not defined: {name}")

    def __iter__(self) -> Generator[dict, Any, None]:
        for block in self.__blocks:
            if isinstance(block, Collection):
                yield from block
            else:
                yield block


def collect(func: Callable) -> Callable:
    """
    This is a decorator used to create a collection. Collections are similar
    to Terraform modules except the resources are included in the root
    module rather than under a named module.

    Decorated functions should:

    * Accept a single argument "var"
    * Yield pretf.api.tf blocks
        * Optionally including "variable" blocks to define inputs
        * Optionally including "output" blocks to define outputs

    When using a collection, any required inputs defined by variable blocks
    must be passed in as keyword arguments. Any outputs defined by output
    blocks can be accessed as attributes of the collection.

    """

    @wraps(func)
    def wrapped(**kwargs: dict) -> Collection:

        # Create a store to track variables.
        var_store = VariableStore()

        # Load variable values from kwargs passed into the collection function.
        for key, value in kwargs.items():
            var_value = VariableValue(name=key, value=value, source="kwargs")
            var_store.add(var_value)

        # Call the collection function, passing in "path", "terraform" and "var" if required.
        gen = call_pretf_function(func=func, var=var_store.proxy(func.__name__))

        blocks = []
        outputs = {}

        yielded = None
        while True:

            try:
                yielded = gen.send(yielded)
            except StopIteration:
                break

            for block in unwrap_yielded(yielded):

                # Use variable blocks to update the variable store.
                var_def = None
                for var_def in get_variable_definitions_from_block(
                    block, func.__name__
                ):
                    var_store.add(var_def)

                # Use output blocks to update the output values.
                output = None
                for output in get_outputs_from_block(block):
                    name = output["name"]
                    value = output["value"]
                    outputs[name] = value

                # Use any other blocks in the resulting JSON.
                if not var_def and not output:
                    blocks.append(block)

        return Collection(blocks, outputs)

    return wrapped
