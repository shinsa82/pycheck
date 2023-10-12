"""
Examples in Sato's paper.
"""
from pycheck import spec
from typing import Any


@spec('(f:(x:int -> { r:int | lambda x,r: r >=x }), y:int) -> { s:int | lambda s,y: s >= y }')
def fsum(f: Any, y: int) -> int:
    """returns f(1) + ... + f(y)"""
    if y <= 0:
        return 0
    else:
        return f(y) + fsum(f, y - 1)


@spec('x:int -> { r:int | lambda x,r: r >=x }')
def double_(x: int) -> int:
    "function double(), but postfixed by _ to avoid name conflict."
    return x + x


@spec('x:int -> { r:int | lambda x,r: r >=x }')
def main(x: int) -> int:
    return fsum(double_, x)
