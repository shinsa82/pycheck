"""
Testcases for typecheck() function.
"""
from functions import inc, inc_bad, inc_callable
from pytest import raises

from pycheck import typecheck


def test_typecheck_pass_01():
    assert typecheck(3, int)


def test_typecheck_fail_01():
    assert not typecheck(3, str)
