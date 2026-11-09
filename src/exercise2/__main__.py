import argparse
from pathlib import Path

from dbs2.dbms import DBMS, ColumnDefinition, ColumnType
from dbs2.dbms.utils.relation_utils import load_csv, print_all_blocks

from .tpmms import TPMMS


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TPMMS example.")
    parser.add_argument(
        "input", nargs="?", type=Path, default=Path("tests/resources/exercise2/input.csv")
    )
    parser.add_argument("--sort-column", type=int, choices=range(3), default=0)
    parser.add_argument(
        "--sort", action="store_true", help="Run the sort after implementing TPMMS."
    )
    args = parser.parse_args()

    dbms = DBMS(total_blocks=3, block_capacity=2)
    columns = ColumnDefinition(ColumnType.INTEGER, ColumnType.STRING, ColumnType.DOUBLE)
    input_relation = dbms.create_relation(columns)
    print(f'Using "{args.input}" as input relation.')
    try:
        with args.input.open(encoding="utf-8", newline="") as stream:
            load_csv(input_relation, dbms.block_manager, stream)
    except (OSError, ValueError, IndexError) as error:
        parser.error(str(error))

    print("Input relation:")
    print_all_blocks(input_relation)
    output_relation = dbms.create_relation(columns)
    operation = TPMMS(dbms.block_manager, args.sort_column)

    if args.sort:
        operation.execute(input_relation, output_relation)

    print("Output relation:")
    print_all_blocks(output_relation)


if __name__ == "__main__":
    main()
