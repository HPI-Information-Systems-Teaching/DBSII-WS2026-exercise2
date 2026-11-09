from dataclasses import dataclass


@dataclass
class IOCostTracker:
    input_cost: int = 0
    output_cost: int = 0

    @property
    def io_cost(self) -> int:
        return self.input_cost + self.output_cost

    def do_input(self) -> None:
        self.input_cost += 1

    def do_output(self) -> None:
        self.output_cost += 1
