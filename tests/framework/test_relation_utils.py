from contextlib import closing
from io import StringIO

import pytest

from dbs2.dbms import DBMS, ColumnDefinition, ColumnType, Relation, Tuple
from dbs2.dbms.utils.relation_utils import equal_content, fill, load_csv, tuple_iterator


def make_relation(dbms: DBMS, values: list[int]) -> Relation:
    relation = dbms.create_relation(ColumnDefinition(ColumnType.INTEGER))
    with fill(relation, dbms.block_manager) as filler:
        for value in values:
            filler.add(Tuple(1, value))
    return relation


def test_fill() -> None:
    dbms = DBMS(total_blocks=3, block_capacity=2)
    relation = make_relation(dbms, [1, 2, 3])
    assert dbms.block_manager.used_blocks == 0
    blocks = list(relation)
    assert len(blocks) == 2
    with dbms.block_manager.load(blocks[0]) as block:
        assert block.size == 2
        assert list(block) == [Tuple(1, 1), Tuple(1, 2)]
    with dbms.block_manager.load(blocks[1]) as block:
        assert block.size == 1
        assert block[0] == Tuple(1, 3)
    assert dbms.block_manager.used_blocks == 0


def test_tuple_iterator() -> None:
    dbms = DBMS(total_blocks=3, block_capacity=2)
    relation = make_relation(dbms, [1, 2, 3, 4, 5])
    assert list(tuple_iterator(relation, dbms.block_manager)) == [
        Tuple(1, value) for value in range(1, 6)
    ]
    assert dbms.block_manager.used_blocks == 0


@pytest.mark.parametrize(
    ("left_values", "right_values", "expected"),
    [
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], True),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6], False),
        ([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5], False),
        ([1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], False),
        ([], [], True),
        ([], [1], False),
    ],
)
def test_equal_content_releases_memory(left_values, right_values, expected) -> None:
    dbms = DBMS(total_blocks=3, block_capacity=2)
    left = make_relation(dbms, left_values)
    right = make_relation(dbms, right_values)
    assert equal_content(dbms.block_manager, left, right) is expected
    assert dbms.block_manager.used_blocks == 0


def test_closing_tuple_iterator_early_releases_block() -> None:
    dbms = DBMS(total_blocks=1, block_capacity=2)
    relation = make_relation(dbms, [1, 2, 3])
    with closing(tuple_iterator(relation, dbms.block_manager)) as rows:
        assert next(rows) == Tuple(1, 1)
        assert dbms.block_manager.used_blocks == 1
    assert dbms.block_manager.used_blocks == 0


def test_load_csv_selects_columns_and_handles_quoted_fields() -> None:
    dbms = DBMS(total_blocks=1, block_capacity=2)
    relation = dbms.create_relation(
        ColumnDefinition(ColumnType.INTEGER, ColumnType.STRING, ColumnType.DOUBLE)
    )
    stream = StringIO('name;ignored;number;score\n"a;b";x; 3; 1.5\n"a\nb";y;4;2.5\n')
    count = load_csv(
        relation, dbms.block_manager, stream,
        column_indices=[2, 0, 3], delimiter=";", contains_header=True,
    )
    assert count == 3
    assert not stream.closed
    assert list(tuple_iterator(relation, dbms.block_manager)) == [
        Tuple(3, 3, "a;b", 1.5), Tuple(3, 4, "a\nb", 2.5)
    ]
    assert dbms.block_manager.used_blocks == 0


def test_invalid_csv_releases_memory() -> None:
    dbms = DBMS(total_blocks=1, block_capacity=2)
    relation = dbms.create_relation(ColumnDefinition(ColumnType.INTEGER))
    with pytest.raises(ValueError):
        load_csv(relation, dbms.block_manager, StringIO("1\ninvalid\n"))
    assert dbms.block_manager.used_blocks == 0


def test_clear_deletes_disk_references_and_relation_can_be_reused() -> None:
    dbms = DBMS(total_blocks=1, block_capacity=2)
    relation = make_relation(dbms, [1, 2, 3])
    references = list(relation)
    relation.clear()
    assert relation.estimated_block_count() == 0
    assert dbms.block_manager.used_blocks == 0
    for reference in references:
        with pytest.raises(RuntimeError, match="stale"):
            dbms.block_manager.load(reference)
    with fill(relation, dbms.block_manager) as filler:
        filler.add(Tuple(1, 7))
    assert list(tuple_iterator(relation, dbms.block_manager)) == [Tuple(1, 7)]
