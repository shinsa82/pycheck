# ex02.py
from pycheck import ArgsType, RefinementType, spec


@spec(ArgsType(x=int) >> RefinementType(int, 'r', lambda x, r: r > x))
def inc(x: int) -> int:
    return x + 1
