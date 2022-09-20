from collections.abc import Callable
from typing import Annotated

from pytest import raises

from pycheck import check


def ho_func(x: int, f: Callable[[int], int]) -> int:
    return f(x)

def ho_func2(x: int, f: Callable[[int], int]) -> bool:
    return f(x) != f(x)

def test_func_type1():
    assert check(ho_func, max_iter=1)
    assert False

def test_func_type2():
    assert check(ho_func2, max_iter=100)
    assert False, 'debug'