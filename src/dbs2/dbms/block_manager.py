from .block import Block
from .utils.io_cost_tracker import IOCostTracker


class OutOfMemoryError(MemoryError):
    """No free blocks remain in the simulated memory."""


class BlockManager:
    """Manage loaded blocks, disk references, and simulated disk I/O."""

    def __init__(self, total_blocks: int, block_capacity: int) -> None:
        if total_blocks <= 0 or block_capacity <= 0:
            raise ValueError("Block count and capacity must be positive")
        self.total_blocks = total_blocks
        self.block_capacity = block_capacity
        self._active_blocks: set[Block] = set()
        self.io_cost_tracker: IOCostTracker | None = None

    @property
    def used_blocks(self) -> int:
        return len(self._active_blocks)

    @property
    def free_blocks(self) -> int:
        return self.total_blocks - self.used_blocks

    def allocate(self, in_memory: bool) -> Block:
        """Allocate an empty loaded block or an unloaded disk reference."""
        if in_memory:
            self._require_free_block()
        block = Block(self, self.block_capacity)
        if in_memory:
            self._active_blocks.add(block)
        return block

    def release(self, block: Block) -> None:
        """Free a loaded block. The supplied reference becomes stale."""
        self._check_owner(block)
        block._check_loaded()
        self._active_blocks.remove(block)
        block._stale = True

    def load(self, block_reference: Block) -> Block:
        """Return a loaded copy of a disk block; count one disk read."""
        self._check_owner(block_reference)
        if block_reference.is_loaded:
            raise RuntimeError("Block is already loaded in memory")
        self._require_free_block()
        block = block_reference._copy()
        self._active_blocks.add(block)
        if self.io_cost_tracker is not None:
            self.io_cost_tracker.do_input()
        return block

    def delete_on_disk(self, block_reference: Block) -> None:
        """Delete an unloaded disk block. Its reference becomes stale."""
        self._check_owner(block_reference)
        if block_reference.is_loaded:
            raise RuntimeError("Block is not on disk")
        block_reference._stale = True

    def write_to_disk(self, block: Block) -> Block:
        """Return a disk copy and count one write. The loaded block stays loaded."""
        self._check_owner(block)
        block._check_loaded()
        reference = block._copy()
        if self.io_cost_tracker is not None:
            self.io_cost_tracker.do_output()
        return reference

    def _require_free_block(self) -> None:
        if self.free_blocks == 0:
            raise OutOfMemoryError("No free memory blocks")

    def _check_owner(self, block: Block) -> None:
        if block._manager is not self:
            raise ValueError("Block belongs to another block manager")
        block._check_valid()

    def __repr__(self) -> str:
        return f"BlockManager[free={self.free_blocks}/{self.total_blocks}]"
