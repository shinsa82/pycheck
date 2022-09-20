from typing import Iterable


def inc(x: int) -> int:
    return x + 1


x: Iterable[int] = map(inc, [1, 2, 3])

reveal_type(map)
