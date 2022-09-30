"""
Module for configuration and execution context.
"""
from dataclasses import dataclass
from typing import NewType


@dataclass
class Config:
    "class for storing PyCheck configuration."
    max_iteration: int = 100  # max number of success iterations.
    # max number of tries (including both success and fail) for avoiding infinite loop.
    max_tries: int = 10000
    # max number of tries until typechecker give up checking due to many assumption failures.
    seed_nbits: int = 64  # number of bits of the random seed.
    # explicitly specified seed. used for reproductive result.
    seed: int = None
    stat: bool = False  # records detailed stats during opcode execution.

    # def __init__(self, max_iteration=100, max_tries=10000, seed_nbits=64, seed=None):
    #     self.max_iteration = max_iteration
    #     self.max_tries = max_tries
    #     self.seed_nbits = seed_nbits
    #     self.seed = seed

    # def __str__(self):
    #     max_iteration = self.max_iteration
    #     seed_nbits = self.seed_nbits
    #     seed = self.seed
    #     return f"Config({max_iteration=}, {seed_nbits=}, {seed=})"


# dependent-type context: includes preceding variables' values.
# Let us consider the following type, typecheck `y` or generate a value of `y` requires
# the value of `x`:
#   ( x: int, y: { y: int | y > x } ) -> int
# The Context contains the information.
Context = NewType("Context", dict)

__all__ = ["Config", "Context"]
