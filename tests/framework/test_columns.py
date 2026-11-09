import pytest

from dbs2.dbms import ColumnDefinition, ColumnRange, ColumnType, Tuple


def test_typed_tuple_checks_values() -> None:
    columns = ColumnDefinition(ColumnType.INTEGER, ColumnType.STRING, ColumnType.DOUBLE)
    row = columns.create_tuple()
    row[0], row[1], row[2] = 1, "one", 1.0
    assert row == Tuple(3, 1, "one", 1.0)
    with pytest.raises(TypeError):
        row[0] = True
    with pytest.raises(TypeError):
        row[2] = 1
    with pytest.raises(IndexError):
        row[3] = "extra"
    row[0] = None
    with pytest.raises(TypeError):
        columns.get_column_key(0)(row)


def test_copy_into_respects_nonzero_source_and_target_offsets() -> None:
    source = Tuple(4, 10, 20, 30, 40)
    target = Tuple(4)
    source.copy_into(target, ColumnRange(1, 2), ColumnRange(2, 3))
    assert target == Tuple(4, None, None, 20, 30)
    source.copy_into(source, ColumnRange(0, 2), ColumnRange(1, 3))
    assert source == Tuple(4, 10, 10, 20, 30)
    assert Tuple(3, 1) == Tuple(3, 1, None, None)


def test_column_ranges_and_concatenation() -> None:
    column_range = ColumnRange.from_column_count(2) + 1
    assert list(column_range) == [1, 2]
    assert list(column_range.iterate(Tuple(3, 1, 2, 3))) == [2, 3]
    assert ColumnRange.from_column_count(0).column_count == 0
    assert list(ColumnRange.from_column_count(0)) == []
    assert ColumnDefinition(ColumnType.INTEGER) + ColumnDefinition(ColumnType.STRING) == (
        ColumnDefinition(ColumnType.INTEGER, ColumnType.STRING)
    )
