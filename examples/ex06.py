import pycheck
from pycheck import check
import logging

logging.basicConfig(
    level=logging.INFO,
    format='{asctime} [{levelname:.4}] {name}: {message}',
    style='{', force=True)


def max_(x: int, y: int) -> int:
    "sample multi-argument function."
    return max(x, y)


print(f'pycheck version = {pycheck.__version__}')
check(max_, {'x': int, 'y': int}, int)
