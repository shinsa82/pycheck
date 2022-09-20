"test of check(), the top-level typecheck method."
from typing import Annotated
from importlib.metadata import version
from .functions import add, foo, inc, inc_bad, inc_callable, monus
from pytest import raises

import pycheck
from pycheck import check
from pycheck.typecheck import typecheck

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='{asctime} [{levelname:.4}] {name}: {message}',
#     style='{', force=True)


def test_version():
    # print(__name__)
    # print(sys.path)
    assert pycheck.__version__ == version('pycheck')


def test_simple_pass_01():
    assert pycheck.check(inc)


def test_simple_fail_02():
    assert not pycheck.check(inc_bad)


def test_typecheck_pass_01():
    assert typecheck(3, int)


def test_typecheck_pass_02():
    assert check(add)


def test_typecheck_pass_03():
    assert check(foo)


def test_typecheck_pass_04():
    assert check(monus)
