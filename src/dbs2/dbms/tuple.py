from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .column_range import ColumnRange


class Tuple:
    """A mutable row. Use ColumnDefinition.create_tuple for type checking."""

    def __init__(self, column_count: int, *values: Any) -> None:
        if column_count < 0 or len(values) > column_count:
            raise ValueError("Values do not fit the column count")
        self._values = list(values) + [None] * (column_count - len(values))

    @property
    def column_count(self) -> int:
        return len(self._values)

    def __getitem__(self, column_index: int) -> Any:
        return self._values[column_index]

    def __setitem__(self, column_index: int, value: Any) -> None:
        self._values[column_index] = value

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def copy_into(
        self,
        other: Tuple,
        source_range: ColumnRange | None = None,
        target_range: ColumnRange | None = None,
    ) -> None:
        """Copy values from source_range into the other row's target_range."""
        if source_range is None:
            source_range = ColumnRange.from_column_count(self.column_count)
        if target_range is None:
            target_range = ColumnRange.from_column_count(source_range.column_count)
        if source_range.column_count != target_range.column_count:
            raise ValueError("Source and target ranges must have the same size")
        if source_range.end_column_index >= self.column_count:
            raise IndexError("Source range exceeds the column count")
        if target_range.end_column_index >= other.column_count:
            raise IndexError("Target range exceeds the column count")
        values = list(source_range.iterate(self))
        for index, value in zip(target_range, values):
            other[index] = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tuple):
            return NotImplemented
        return self._values == other._values

    def __repr__(self) -> str:
        return f"Tuple[{', '.join(map(str, self._values))}]"
