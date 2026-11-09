from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .tuple import Tuple


class ColumnType(Enum):
    INTEGER = int
    DOUBLE = float
    STRING = str

    def from_string(self, value: str) -> int | float | str:
        return self.value(value)

    def is_compatible(self, value: Any) -> bool:
        return value is None or type(value) is self.value

    def require_compatibility(self, value: Any) -> None:
        if not self.is_compatible(value):
            raise TypeError(
                f"Column type {self.name} does not match {type(value).__name__}"
            )


@dataclass(frozen=True, init=False)
class ColumnDefinition:
    column_types: tuple[ColumnType, ...]

    def __init__(self, *column_types: ColumnType) -> None:
        if any(not isinstance(column_type, ColumnType) for column_type in column_types):
            raise TypeError("Expected ColumnType values")
        object.__setattr__(self, "column_types", column_types)

    @property
    def column_count(self) -> int:
        return len(self.column_types)

    def get_column_type(self, column_index: int) -> ColumnType:
        return self.column_types[column_index]

    def get_column_key(self, column_index: int) -> Callable[[Tuple], Any]:
        """Return a reusable sorting key for the given column."""
        column_type = self.get_column_type(column_index)

        def key(row: Tuple) -> Any:
            value = row[column_index]
            column_type.require_compatibility(value)
            if value is None:
                raise TypeError("Cannot sort an unset column value")
            return value

        return key

    def create_tuple(self) -> Tuple:
        """Create a row that checks values against their column types."""
        return TypedTuple(self)

    def __add__(self, other: ColumnDefinition) -> ColumnDefinition:
        return ColumnDefinition(*self.column_types, *other.column_types)


class TypedTuple(Tuple):
    def __init__(self, column_definition: ColumnDefinition) -> None:
        super().__init__(column_definition.column_count)
        self.column_definition = column_definition

    def __setitem__(self, column_index: int, value: Any) -> None:
        self.column_definition.get_column_type(column_index).require_compatibility(value)
        super().__setitem__(column_index, value)
