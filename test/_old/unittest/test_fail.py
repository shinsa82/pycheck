import logging
import sys

from functions import inc, inc_callable
from pytest import raises

import pycheck

logging.basicConfig(
    level=logging.DEBUG,
    format='{asctime} [{levelname:.4}] {name}: {message}',
    style='{', force=True)


def test_simple_fail_01():
    with raises(TypeError):
        pycheck.check(3)


def test_simple_fail_02():
    with raises(TypeError):
        pycheck.check(inc_callable)
