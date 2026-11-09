from abc import ABC, abstractmethod

from .block_manager import BlockManager
from .relation import Relation


class RelationSizeExceedsCapacityError(ValueError):
    """The relation exceeds the algorithm's capacity for the available memory."""


class Operation(ABC):
    def __init__(self, block_manager: BlockManager) -> None:
        self.block_manager = block_manager


class UnaryOperation(Operation):
    @abstractmethod
    def execute(self, input_relation: Relation, output_relation: Relation) -> None:
        pass

    @abstractmethod
    def estimated_io_cost(self, input_relation: Relation) -> int:
        pass


class BinaryOperation(Operation):
    @abstractmethod
    def execute(
        self,
        left_input_relation: Relation,
        right_input_relation: Relation,
        output_relation: Relation,
    ) -> None:
        pass

    @abstractmethod
    def estimated_io_cost(
        self, left_input_relation: Relation, right_input_relation: Relation
    ) -> int:
        pass
