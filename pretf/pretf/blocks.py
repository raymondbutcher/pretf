from collections.abc import Iterable
from types import ModuleType
from typing import Any, Dict, Generator, List, Optional, Union


class BlockModule(ModuleType):
    def __init__(
        self, block_type: str, labels: Optional[List[str]] = None, needs: int = 0
    ):
        if labels is None:
            labels = []

        self.block_type = block_type
        self.labels = labels
        self.needs = needs

        # Also be a module.
        name = ".".join([__name__, block_type] + labels)
        self.__path__ = name
        super().__init__(name)

    def __call__(self, *bodies: Dict[str, Any], **kwargs: Dict[str, Any]) -> "Block":
        return Block(self.block_type, self.labels, {})(*bodies, **kwargs)

    def __getattr__(self, name: str) -> Union["BlockModule", "Block"]:
        if name.startswith("__"):
            raise AttributeError(name)
        if self.needs == 0:
            return getattr(Block(self.block_type, self.labels, {}), name)
        elif self.needs == 1:
            return Block(self.block_type, self.labels + [name], {})
        else:
            return self.__class__(self.block_type, self.labels + [name], self.needs - 1)

    __getitem__ = __getattr__


class Block(Iterable):
    def __init__(self, block_type: str, labels: List[str], body: Dict[str, Any]):
        self._block_type = block_type
        self._labels = labels
        self._body = body

    def __call__(self, *bodies: Dict[str, Any], **kwargs: Dict[str, Any]) -> "Block":
        """
        Returns a new block with the specified body.

        """

        body: Dict[str, Any] = {}
        for each in bodies:
            body.update(each)
        body.update(kwargs)
        return self.__class__(self._block_type, self._labels, body)

    def __iter__(self) -> Generator[tuple, None, None]:
        if self._labels:
            result: dict = {}
            here = result
            for label in self._labels[:-1]:
                here[label] = {}
                here = here[label]
            here[self._labels[-1]] = self._body
        else:
            result = self._body
        yield (self._block_type, result)

    def _get_expression(self, name: Optional[str] = None) -> Union["Interpolated", str]:
        if self._block_type == "data":
            if len(self._labels) < 2:
                raise ValueError("data blocks require 2 labels")
            parts = [self._block_type] + list(self._labels)
        elif self._block_type == "locals":
            if len(self._labels) < 1 and not name:
                raise ValueError("locals blocks require 1 label")
            parts = ["local"] + list(self._labels)
        elif self._block_type == "module":
            if len(self._labels) < 1:
                raise ValueError("module blocks require 1 label")
            parts = [self._block_type] + list(self._labels)
        elif self._block_type == "output":
            if len(self._labels) < 1:
                raise ValueError("output blocks require 1 label")
            parts = [self._block_type] + list(self._labels)
        elif self._block_type == "provider":
            if len(self._labels) < 1:
                raise ValueError("provider blocks require 1 label")
            parts = list(self._labels)
            if name == "alias" or not name:
                if self._body:
                    alias = self._body.get("alias") or "default"
                    if alias != "default":
                        parts.append(alias)
                return ".".join(parts)
        elif self._block_type == "resource":
            if len(self._labels) < 2:
                raise ValueError("resource blocks require 2 labels")
            parts = list(self._labels)
        elif self._block_type == "variable":
            if len(self._labels) < 1:
                raise ValueError("variable blocks require 1 label")
            parts = ["var"] + self._labels
        else:
            parts = [self._block_type] + list(self._labels)

        if name:
            parts.append(name)

        return Interpolated(".".join(parts))

    def __getattr__(self, name: str) -> Union["Interpolated", str]:
        if name.startswith("__"):
            raise AttributeError(name)
        return self._get_expression(name)

    __getitem__ = __getattr__

    def __repr__(self) -> str:
        parts: List[Any] = [self._block_type]
        parts.extend(self._labels)
        if self._body is not None:
            parts.append(self._body)
        return f"block({', '.join(repr(part) for part in parts)})"

    def __str__(self) -> str:
        return str(self._get_expression())


class Interpolated:
    def __init__(self, value: str):
        self.__value = value

    def __eq__(self, other: Any) -> bool:
        return str(self) == other

    def __getattr__(self, attr: str) -> "Interpolated":
        return type(self)(self.__value + "." + attr)

    def __getitem__(self, index: int) -> "Interpolated":
        return type(self)(f"{self.__value}[{index}]")

    def __repr__(self) -> str:
        return f"Interpolated({repr(self.__value)})"

    def __str__(self) -> str:
        return "${" + self.__value + "}"


data = BlockModule("data", needs=2)
locals = BlockModule("locals", needs=0)
module = BlockModule("module", needs=1)
output = BlockModule("output", needs=1)
provider = BlockModule("provider", needs=1)
resource = BlockModule("resource", needs=2)
variable = BlockModule("variable", needs=1)

__all__ = ["data", "locals", "module", "output", "provider", "resource", "variable"]
