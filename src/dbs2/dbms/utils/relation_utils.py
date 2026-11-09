from __future__ import annotations

import csv
import sys
from collections.abc import Generator, Sequence
from contextlib import closing
from itertools import zip_longest
from types import TracebackType
from typing import TextIO

from ..block import Block
from ..block_manager import BlockManager
from ..relation import Relation
from ..tuple import Tuple


def print_all_blocks(relation: Relation, output_stream: TextIO | None = None) -> None:
    for block in relation:
        print(block, file=output_stream if output_stream is not None else sys.stdout)


def load_csv(
    relation: Relation,
    block_manager: BlockManager,
    csv_input_stream: TextIO,
    column_indices: Sequence[int] | None = None,
    delimiter: str = ",",
    contains_header: bool = False,
) -> int:
    """Append CSV records as unloaded blocks; return the number of records read.

    Column indices select and reorder input columns. Extra columns are ignored.
    The count includes the header when present. The caller owns the stream.
    """
    if column_indices is None:
        column_indices = range(relation.columns.column_count)
    if len(column_indices) != relation.columns.column_count:
        raise ValueError("Select one input column per relation column")
    if any(index < 0 for index in column_indices):
        raise ValueError("Column indices must be nonnegative")

    records = 0
    with fill(relation, block_manager) as filler:
        for fields in csv.reader(csv_input_stream, delimiter=delimiter):
            if not fields:
                continue
            records += 1
            if contains_header and records == 1:
                continue
            row = relation.columns.create_tuple()
            for index, source_index in enumerate(column_indices):
                column_type = relation.columns.get_column_type(index)
                row[index] = column_type.from_string(fields[source_index].strip())
            filler.add(row)
    return records


def fill(relation: Relation, block_manager: BlockManager) -> RelationFiller:
    """Fill a relation in a with block, using one memory block at a time.

    For setup and tests only; do not call this helper in the exercise solution.
    You may take inspiration from its implementation.
    """
    return RelationFiller(relation, block_manager)


class RelationFiller:
    """Append rows to a relation. For setup and tests only."""

    def __init__(self, relation: Relation, block_manager: BlockManager) -> None:
        if relation.block_manager is not block_manager:
            raise ValueError("Relation belongs to another block manager")
        self._block_manager = block_manager
        self._block_input = relation.get_block_input()
        self._current_block: Block | None = None
        self._closed = False

    def add(self, row: Tuple) -> None:
        if self._closed:
            raise RuntimeError("Relation filler is closed")
        if self._current_block is not None and self._current_block.is_full:
            self._block_input.move(self._current_block)
            self._current_block = None
        if self._current_block is None:
            self._current_block = self._block_manager.allocate(in_memory=True)
        self._current_block.append(row)

    def close(self) -> None:
        if self._closed:
            return
        if self._current_block is not None:
            if self._current_block.is_empty:
                self._current_block.close()
            else:
                self._block_input.move(self._current_block)
            self._current_block = None
        self._closed = True

    def __enter__(self) -> RelationFiller:
        if self._closed:
            raise RuntimeError("Relation filler is closed")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


def tuple_iterator(
    relation: Relation, block_manager: BlockManager
) -> Generator[Tuple, None, None]:
    """Iterate over tuples, loading one block at a time.

    For setup and tests only; do not call this helper in the exercise solution.
    If stopping early, close the iterator to release its current block.
    """
    for reference in relation:
        with block_manager.load(reference) as block:
            yield from block


def equal_content(
    block_manager: BlockManager, relation1: Relation, relation2: Relation
) -> bool:
    """Compare tuple values and order, releasing blocks even on a mismatch.

    For tests only; do not call this helper in the exercise solution.
    """
    missing = object()
    with (
        closing(tuple_iterator(relation1, block_manager)) as left,
        closing(tuple_iterator(relation2, block_manager)) as right,
    ):
        return all(a == b for a, b in zip_longest(left, right, fillvalue=missing))
