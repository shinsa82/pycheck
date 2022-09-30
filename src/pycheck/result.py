"dataclass for storing typechecking results."
from dataclasses import dataclass, field


@dataclass
class Result:
    "dataclass for storing typechecking results."
    well_typed: bool = field(default=None)
