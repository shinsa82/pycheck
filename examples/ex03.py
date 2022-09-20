import pycheck
from pycheck import check
import logging

logging.basicConfig(
    level=logging.INFO,
    format='{asctime} [{levelname:.4}] {name}: {message}',
    style='{', force=True)


def dec(x: int) -> int:
    if x > 0:
        return x-1
    raise ValueError('x should be positive.')

def is_positive(x: int) -> bool:
    return x > 0

def is_zero_or_positive(x: int) -> bool:
    return x >= 0

print(f'pycheck version = {pycheck.__version__}')
check(dec, (int, is_positive), (int, is_zero_or_positive))
