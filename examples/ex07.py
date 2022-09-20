"""example of list types"""
import pycheck
from pycheck import check
import logging

logging.basicConfig(
    level=logging.INFO,
    format='{asctime} [{levelname:.4}] {name}: {message}',
    style='{', force=True)


def at(x: list[int], y:int) -> int:
    return x[y]


print(f'pycheck version = {pycheck.__version__}')
check(at, list[int], int)
