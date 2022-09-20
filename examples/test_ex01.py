# test_ex01.py
from pycheck import check


def inc(x: int) -> int:
    return x + 1


def test_inc():
    assert check(inc)  # typecheck inc() by a random test
