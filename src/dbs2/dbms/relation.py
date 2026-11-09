from collections.abc import Iterator

from .block import Block
from .block_input import BlockInput
from .block_manager import BlockManager
from .column_definition import ColumnDefinition


class Relation:
    """A collection of disk block references with a common column definition."""

    def __init__(self, block_manager: BlockManager, columns: ColumnDefinition) -> None:
        self.block_manager = block_manager
        self.columns = columns
        self._blocks: list[Block] = []
        self._block_input = BlockInput(self)

    def estimated_block_count(self) -> int:
        return len(self._blocks)

    def clear(self) -> None:
        """Remove this relation's blocks from disk."""
        for block in self._blocks:
            self.block_manager.delete_on_disk(block)
        self._blocks.clear()

    def __iter__(self) -> Iterator[Block]:
        return iter(self._blocks)

    def get_block_input(self) -> BlockInput:
        """Return an input that appends loaded blocks to this relation."""
        return self._block_input
