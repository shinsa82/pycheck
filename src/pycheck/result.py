"dataclass for storing typechecking results."
from dataclasses import dataclass, field


@dataclass
class Result:
    "dataclass for storing typechecking results."
    well_typed: bool = field(default=None)
    failed_at: int = None
    max_iter: int = None
    retry: int = None  # retries of generation

    def __str__(self):
        if self.well_typed:
            return f"well-typed = {self.well_typed}, passed {self.max_iter}/{self.max_iter} ({self.retry} retries)"
        # untyped
        return f"well-typed = {self.well_typed}, failed at iteration {self.failed_at}/{self.max_iter}"
