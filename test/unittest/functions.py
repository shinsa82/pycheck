"""
Type-annotated function that are used by tests.

Run `mypy functions.py` to (simply) typecheck functions.
"""
from collections.abc import Callable
from types import LambdaType
from typing import Annotated

from pycheck import Refinement


def inc(x: int) -> int:
    return x+1


def inc_bad(x: int) -> int:
    if x == 0:
        return 'bad'
    return x+1


def add(x: int, y: int) -> int:
    return x + y + 1


def foo(x: int, y: Annotated[int, Refinement('y', lambda x, y: y >= x)]) -> int:
    return x + y


def monus(
    x: Annotated[int, Refinement('x', lambda x: x >= 0)],
    y: Annotated[int, Refinement('y', lambda x, y: y >= 0)]
) -> Annotated[int, Refinement('z', lambda x, y, z: z >= 0)]:
    "saturated subtraction"
    return max(x-y, 0)


inc_callable: Callable[[int], int] = lambda x: x+1

# inc_lambda: LambdaType = lambda x: x+1 # mypy typecheck fails
