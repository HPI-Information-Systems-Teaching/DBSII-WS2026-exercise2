from dbs2.dbms import Relation

from .sort_operation import SortOperation


class TPMMS(SortOperation):
    def estimated_io_cost(self, input_relation: Relation) -> int:
        raise NotImplementedError("TODO")

    def sort(self, input_relation: Relation, output_relation: Relation) -> None:
        raise NotImplementedError("TODO")
