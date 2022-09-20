import pycheck
from pycheck import check
import logging

logging.basicConfig(
    level=logging.INFO,
    format='{asctime} [{levelname:.4}] {name}: {message}',
    style='{', force=True)


def inc(x: int) -> int:
    """function that have a bug."""
    if x == 0:
        return 'bad return value'
    return x+1


print(f'pycheck version = {pycheck.__version__}')
check(inc, int, int)
