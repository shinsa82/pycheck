"""
tests for opcodes and executor.
"""
from pycheck.opcode import Evaluator, IsIns, Or
import pytest


@pytest.fixture
def ex() -> Evaluator:
    return Evaluator()


def test_IsIns(ex):
    "Check if |- 3 : int"
    assert ex.evaluate([IsIns(3, int)])


def test_Or_1(ex):
    "Check if |- 3 : (str | int), checking shortcut evaluation"
    assert ex.evaluate([
        Or(IsIns(3, str), IsIns(3, int))
    ])


def test_Or_2(ex):
    "Check if |- 3 : (int | str), checking shortcut evaluation"
    assert ex.evaluate([
        Or(IsIns(3, int), IsIns(3, str))
    ])
