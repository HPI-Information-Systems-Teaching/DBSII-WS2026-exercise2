from collections.abc import Callable, Sequence
from typing import Any

from ..block import Block
from ..tuple import Tuple


def sort_blocks(blocks: Sequence[Block], key: Callable[[Tuple], Any]) -> None:
    """Sort tuples in loaded blocks in place using the given column key."""
    rows = sorted((row for block in blocks for row in block), key=key)
    offset = 0
    for block in blocks:
        block.clear()
        for row in rows[offset : offset + block.capacity]:
            block.append(row)
        offset += block.capacity
