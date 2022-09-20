import pycheck
from pycheck import check
import logging

logging.basicConfig(
    level=logging.INFO,
    format='{asctime} [{levelname:.4}] {name}: {message}',
    style='{', force=True)


def rev(x: str) -> str:
    return ''.join(reversed(x))


print(f'pycheck version = {pycheck.__version__}')
check(rev, str, str)
