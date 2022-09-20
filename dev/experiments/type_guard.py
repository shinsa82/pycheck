"""type-guard by isinstance is actually be considered?"""
from typing import Any


def foo(x: Any) -> str:
    if isinstance(x, str):
        return x + 'bar'
    elif isinstance(x, int):
        return str(x) + 'bar'
    else:
        return 'XXX'
