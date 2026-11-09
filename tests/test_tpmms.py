from pathlib import Path

import pytest

from dbs2.dbms import (
    DBMS,
    ColumnDefinition,
    ColumnType,
    Relation,
    RelationSizeExceedsCapacityError,
)
from dbs2.dbms.utils.relation_utils import equal_content, load_csv
from exercise2.tpmms import TPMMS

RESOURCES = Path(__file__).parent / "resources" / "exercise2"


def load_example(dbms: DBMS, filename: str) -> Relation:
    columns = ColumnDefinition(ColumnType.INTEGER, ColumnType.STRING, ColumnType.DOUBLE)
    relation = dbms.create_relation(columns)
    with (RESOURCES / filename).open(encoding="utf-8", newline="") as stream:
        load_csv(relation, dbms.block_manager, stream)
    return relation


@pytest.mark.parametrize("column_index", [0, 2])
def test_tpmms_sorts_example(column_index: int) -> None:
    dbms = DBMS(total_blocks=3, block_capacity=2)
    input_relation = load_example(dbms, "input.csv")
    output_relation = dbms.create_relation(input_relation.columns)
    operation = TPMMS(dbms.block_manager, column_index)

    with dbms.track_io_cost() as cost:
        assert dbms.block_manager.used_blocks == 0
        operation.execute(input_relation, output_relation)
        assert dbms.block_manager.used_blocks == 0

    control = load_example(dbms, f"sorted_by_col{column_index}.output.csv")
    assert equal_content(dbms.block_manager, control, output_relation)
    assert dbms.block_manager.used_blocks == 0
    assert cost.io_cost == 3 * 6


def test_tpmms_rejects_relation_exceeding_capacity() -> None:
    dbms = DBMS(total_blocks=3, block_capacity=2)
    columns = ColumnDefinition(ColumnType.INTEGER)

    class LargeRelation(Relation):
        def estimated_block_count(self) -> int:
            return 13

        def __iter__(self):
            return iter(dbms.block_manager.allocate(in_memory=False) for _ in range(13))

    input_relation = LargeRelation(dbms.block_manager, columns)
    output_relation = dbms.create_relation(columns)
    operation = TPMMS(dbms.block_manager, 0)

    with pytest.raises(RelationSizeExceedsCapacityError):
        operation.execute(input_relation, output_relation)
    assert dbms.block_manager.used_blocks == 0


def test_tpmms_estimates_io_cost_without_loading_blocks() -> None:
    dbms = DBMS(total_blocks=3, block_capacity=2)
    input_relation = load_example(dbms, "input.csv")
    operation = TPMMS(dbms.block_manager, 0)

    with dbms.track_io_cost() as cost:
        assert operation.estimated_io_cost(input_relation) == 3 * 6

    assert cost.io_cost == 0
    assert dbms.block_manager.used_blocks == 0
