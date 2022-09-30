from typing import Annotated, Callable

f1: Annotated[Callable[[int, int], int], True] = lambda x, y: x - y
