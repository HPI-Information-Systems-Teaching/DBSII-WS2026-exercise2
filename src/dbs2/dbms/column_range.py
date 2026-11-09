from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .tuple import Tuple


@dataclass(frozen=True)
class ColumnRange:
    """A range of column indices, including both endpoints."""

    start_column_index: int
    end_column_index: int

    def __post_init__(self) -> None:
        if self.start_column_index < 0:
            raise ValueError("The first column index must be nonnegative")
        if self.end_column_index < self.start_column_index - 1:
            raise ValueError("Invalid column range")

    @classmethod
    def from_column_count(cls, column_count: int) -> ColumnRange:
        if column_count < 0:
            raise ValueError("The column count must be nonnegative")
        return cls(0, column_count - 1)

    @property
    def column_count(self) -> int:
        return self.end_column_index + 1 - self.start_column_index

    def iterate(self, row: Tuple) -> Iterator[Any]:
        return (row[index] for index in self)

    def __add__(self, displacement: int) -> ColumnRange:
        return ColumnRange(
            self.start_column_index + displacement,
            self.end_column_index + displacement,
        )

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start_column_index, self.end_column_index + 1))
