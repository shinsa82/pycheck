from pycheck import __version__, check_with_type
import logging

logging.basicConfig(
    level=logging.INFO,
    format='{asctime} [{levelname:.4}] {name}: {message}',
    style='{', force=True)


def inc(x: int) -> int:
    return x+1


print(f'pycheck version = {__version__}')
check_with_type(inc, int, int)
