from __future__ import annotations

from typing import TYPE_CHECKING

from .block import Block

if TYPE_CHECKING:
    from .relation import Relation


class BlockInput:
    """Move loaded blocks into a backing relation."""

    def __init__(self, relation: Relation) -> None:
        self._relation = relation

    def move(self, input_block: Block) -> None:
        """Append the block and release it; input_block must not be reused.

        This models passing output to the next operation and adds no disk I/O.
        Use BlockManager.write_to_disk for explicit intermediate disk writes.
        """
        manager = self._relation.block_manager
        manager._check_owner(input_block)
        input_block._check_loaded()
        self._relation._blocks.append(input_block._copy())
        manager.release(input_block)
