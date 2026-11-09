from collections.abc import Iterator
from contextlib import contextmanager

from .block_manager import BlockManager
from .column_definition import ColumnDefinition
from .relation import Relation
from .utils.io_cost_tracker import IOCostTracker


class DBMS:
    def __init__(self, total_blocks: int, block_capacity: int) -> None:
        self.block_manager = BlockManager(total_blocks, block_capacity)

    @property
    def total_blocks(self) -> int:
        return self.block_manager.total_blocks

    @property
    def block_capacity(self) -> int:
        return self.block_manager.block_capacity

    def create_relation(self, columns: ColumnDefinition) -> Relation:
        """Create an empty relation with the given columns."""
        return Relation(self.block_manager, columns)

    @contextmanager
    def track_io_cost(self) -> Iterator[IOCostTracker]:
        """Count disk reads and writes performed within this context."""
        previous = self.block_manager.io_cost_tracker
        tracker = IOCostTracker()
        self.block_manager.io_cost_tracker = tracker
        try:
            yield tracker
        finally:
            self.block_manager.io_cost_tracker = previous
