"""
Example from [Sato et al., 2015].

Simply typed version. See sato_rt.py for refinement-typed version.
"""
from typing import Callable


def fsum(f: Callable[[int], int], n: int) -> int:
    if n <= 0:
        return 0
    else:
        return f(n) + fsum(f, n-1)


def double(n: int) -> int:
    return n+n


def main(n: int) -> int:
    return fsum(double, n)
