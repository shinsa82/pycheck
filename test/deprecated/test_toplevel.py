from importlib.metadata import version

import pytest
from pycheck import __version__, check, spec

skip = pytest.mark.skip


def inc(x: int) -> int:
    return x + 1


@spec('x:int -> int')
def inc_deco(x: int) -> int:
    return x + 1


def test_version():
    assert __version__ == version('pycheck')


@skip(reason='currently undecorated funcs are not supoprted')
def test_undecorated():
    assert check(inc)


def test_check_simply_typed():
    assert check(inc_deco)

# more tests to be apper
