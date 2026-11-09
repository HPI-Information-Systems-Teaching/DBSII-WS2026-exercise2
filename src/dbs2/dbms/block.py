from __future__ import annotations

from collections.abc import Iterator
from copy import deepcopy
from types import TracebackType
from typing import TYPE_CHECKING

from .tuple import Tuple

if TYPE_CHECKING:
    from .block_manager import BlockManager


class Block:
    """A block whose tuples can only be accessed while it is loaded.

    Obtain blocks through BlockManager. A released or deleted block is stale
    and must not be used again. Loaded blocks support the with statement.
    """

    def __init__(self, manager: BlockManager, capacity: int) -> None:
        self._manager = manager
        self._capacity = capacity
        self._tuples: list[Tuple] = []
        self._stale = False

    def _check_valid(self) -> None:
        if self._stale:
            raise RuntimeError("Block is stale")

    def _check_loaded(self) -> None:
        if not self.is_loaded:
            raise RuntimeError("Block is not loaded in memory")

    def _copy(self) -> Block:
        self._check_valid()
        block = Block(self._manager, self.capacity)
        block._tuples = deepcopy(self._tuples)
        return block

    @property
    def is_loaded(self) -> bool:
        self._check_valid()
        return self in self._manager._active_blocks

    @property
    def size(self) -> int:
        self._check_loaded()
        return len(self._tuples)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def is_empty(self) -> bool:
        return self.size == 0

    @property
    def is_full(self) -> bool:
        return self.size >= self.capacity

    def __getitem__(self, tuple_index: int) -> Tuple:
        self._check_loaded()
        return self._tuples[tuple_index]

    def clear(self) -> None:
        self._check_loaded()
        self._tuples.clear()

    def append(self, row: Tuple) -> Tuple:
        if self.is_full:
            raise RuntimeError("Block is full")
        if not isinstance(row, Tuple):
            raise TypeError("Blocks can only contain Tuple instances")
        self._tuples.append(row)
        return row

    def insert(self, tuple_index: int, row: Tuple) -> Tuple:
        if self.is_full:
            raise RuntimeError("Block is full")
        if not isinstance(row, Tuple):
            raise TypeError("Blocks can only contain Tuple instances")
        if not 0 <= tuple_index <= self.size:
            raise IndexError("Invalid tuple index")
        self._tuples.insert(tuple_index, row)
        return row

    def __iter__(self) -> Iterator[Tuple]:
        self._check_loaded()
        return self._iterate()

    def _iterate(self) -> Iterator[Tuple]:
        index = 0
        while True:
            self._check_loaded()
            if index >= len(self._tuples):
                return
            yield self._tuples[index]
            index += 1

    def close(self) -> None:
        """Release this block from memory; this reference becomes stale."""
        self._manager.release(self)

    def __enter__(self) -> Block:
        self._check_loaded()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self._stale:
            self.close()

    def __repr__(self) -> str:
        state = "invalid" if self._stale else f"loaded={self.is_loaded}"
        rows = ",".join(f"\n  {row}" for row in self._tuples)
        return f"Block[{state}]{{{rows}\n}}"
