"""
Example from [Sato et al., 2015].

Refinement-typed version. See sato.py for simply-typed version.
"""
from typing import Annotated, Callable

from pycheck.type.mypy import CallRefType, RefType

fsum_T1 = Annotated[Callable[[int], Annotated[int, RefType('r', lambda x, r: r >= x)]],
                    CallRefType(params=['x'])]


def fsum(f: fsum_T1, y: int) -> Annotated[int, RefType('s', lambda s, y: s >= y)]:
    """returns f(1) + ... + f(y)"""
    if y <= 0:
        return 0
    else:
        return f(y) + fsum(f, y-1)


def double_(x: int) -> Annotated[int, RefType('r', lambda x, r: r >= x)]:
    "function double(), but postfixed by _ to avoid name conflict."
    return x+x


def main(x: int) -> Annotated[int, RefType('r', lambda x, r: r >= x)]:
    return fsum(double_, x)


# uncomment the following lines to know their types.
# reveal_type(fsum)
# reveal_type(double_)
# reveal_type(main)

if __name__ == '__main__':
    print(main(5))
