from abc import abstractmethod

from dbs2.dbms import BlockManager, Relation, UnaryOperation


class SortOperation(UnaryOperation):
    def __init__(self, block_manager: BlockManager, sort_column_index: int) -> None:
        super().__init__(block_manager)
        self.sort_column_index = sort_column_index

    def execute(self, input_relation: Relation, output_relation: Relation) -> None:
        self.sort(input_relation, output_relation)

    @abstractmethod
    def sort(self, input_relation: Relation, output_relation: Relation) -> None:
        """Sort the input relation by sort_column_index into the output relation."""
        pass
