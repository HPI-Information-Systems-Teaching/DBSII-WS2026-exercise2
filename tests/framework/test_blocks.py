import pytest

from dbs2.dbms import DBMS, ColumnDefinition, ColumnType, OutOfMemoryError, Tuple
from dbs2.dbms.utils.block_sorter import sort_blocks


def test_block_lifecycle_and_io_accounting() -> None:
    dbms = DBMS(total_blocks=2, block_capacity=2)
    manager = dbms.block_manager
    relation = dbms.create_relation(ColumnDefinition(ColumnType.INTEGER))

    with dbms.track_io_cost() as cost:
        block = manager.allocate(in_memory=True)
        block.append(Tuple(1, 1))
        reference = manager.write_to_disk(block)
        assert block.is_loaded
        assert not reference.is_loaded
        assert manager.used_blocks == 1
        block.close()
        with pytest.raises(RuntimeError, match="stale"):
            block.append(Tuple(1, 2))
        with pytest.raises(RuntimeError, match="not loaded"):
            _ = reference[0]
        loaded = manager.load(reference)
        assert loaded is not reference
        assert loaded[0] == Tuple(1, 1)
        relation.get_block_input().move(loaded)
        assert manager.used_blocks == 0
        assert (cost.input_cost, cost.output_cost, cost.io_cost) == (1, 1, 2)
        manager.delete_on_disk(reference)


def test_loading_respects_memory_limit_and_failed_reads_are_not_counted() -> None:
    dbms = DBMS(total_blocks=1, block_capacity=2)
    manager = dbms.block_manager
    reference = manager.allocate(in_memory=False)
    with dbms.track_io_cost() as cost:
        with manager.load(reference):
            with pytest.raises(OutOfMemoryError):
                manager.allocate(in_memory=True)
            with pytest.raises(OutOfMemoryError):
                manager.load(reference)
        assert cost.input_cost == 1
    assert manager.free_blocks == 1


def test_iteration_checks_for_released_blocks() -> None:
    manager = DBMS(total_blocks=1, block_capacity=2).block_manager
    block = manager.allocate(in_memory=True)
    block.append(Tuple(1, 1))
    rows = iter(block)
    assert next(rows) == Tuple(1, 1)
    block.close()
    with pytest.raises(RuntimeError, match="stale"):
        next(rows)


def test_disk_snapshot_does_not_change_with_loaded_row() -> None:
    manager = DBMS(total_blocks=2, block_capacity=2).block_manager
    with manager.allocate(in_memory=True) as block:
        block.append(Tuple(1, 1))
        reference = manager.write_to_disk(block)
        block[0][0] = 2
    with manager.load(reference) as loaded:
        assert loaded[0][0] == 1
        loaded[0][0] = 3
    with manager.load(reference) as loaded:
        assert loaded[0][0] == 1


def test_sort_blocks_handles_partial_and_empty_blocks() -> None:
    dbms = DBMS(total_blocks=3, block_capacity=2)
    columns = ColumnDefinition(ColumnType.INTEGER)
    with (
        dbms.block_manager.allocate(in_memory=True) as first,
        dbms.block_manager.allocate(in_memory=True) as second,
        dbms.block_manager.allocate(in_memory=True) as third,
    ):
        first.append(Tuple(1, 3))
        second.append(Tuple(1, 1))
        third.append(Tuple(1, 2))
        sort_blocks([first, second, third], columns.get_column_key(0))
        assert list(first) == [Tuple(1, 1), Tuple(1, 2)]
        assert list(second) == [Tuple(1, 3)]
        assert third.is_empty
    sort_blocks([], columns.get_column_key(0))
    assert dbms.block_manager.used_blocks == 0


def test_block_capacity_and_foreign_manager_are_checked() -> None:
    manager = DBMS(total_blocks=1, block_capacity=1).block_manager
    other_manager = DBMS(total_blocks=1, block_capacity=1).block_manager
    with manager.allocate(in_memory=True) as block:
        block.insert(0, Tuple(1, 1))
        with pytest.raises(RuntimeError, match="full"):
            block.append(Tuple(1, 2))
        with pytest.raises(ValueError, match="another"):
            other_manager.release(block)
        block.clear()
        assert block.is_empty


@pytest.mark.parametrize("method", ["append", "insert"])
def test_blocks_reject_block_references_as_rows(method: str) -> None:
    dbms = DBMS(total_blocks=1, block_capacity=2)
    manager = dbms.block_manager
    relation = dbms.create_relation(ColumnDefinition(ColumnType.INTEGER))
    with manager.allocate(in_memory=True) as source:
        source.append(Tuple(1, 1))
        source.append(Tuple(1, 2))
        relation.get_block_input().move(source)

    with manager.allocate(in_memory=True) as destination:
        reference = next(iter(relation))
        with dbms.track_io_cost() as cost:
            with pytest.raises(TypeError, match="Tuple"):
                if method == "append":
                    destination.append(reference)
                else:
                    destination.insert(0, reference)
        assert destination.is_empty
        assert not reference.is_loaded
        assert manager.used_blocks == 1
        assert cost.io_cost == 0
    assert manager.used_blocks == 0


def test_io_tracking_restores_outer_context_after_exception() -> None:
    dbms = DBMS(total_blocks=1, block_capacity=2)
    reference = dbms.block_manager.allocate(in_memory=False)
    with dbms.track_io_cost() as outer:
        with pytest.raises(ValueError):
            with dbms.track_io_cost() as inner:
                with dbms.block_manager.load(reference):
                    raise ValueError("test")
        with dbms.block_manager.load(reference):
            pass
    assert inner.input_cost == 1
    assert outer.input_cost == 1
    assert dbms.block_manager.io_cost_tracker is None
    assert dbms.block_manager.used_blocks == 0
