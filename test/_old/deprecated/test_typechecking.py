"""
Test for typechecking samples.
"""
import pytest
from pycheck import Config, Context, TypeChecker
from pycheck.opcode import Executor
from pycheck.typecheckers import set_defaults


@pytest.fixture
def tc() -> TypeChecker:
    "returns a TypeChecker with default checkers"
    return set_defaults(TypeChecker(config=Config()))


def test_typecheck_int_OK(tc: TypeChecker) -> None:
    context: Context = Context({})
    codes = tc.typecheck(42, int, context=context)
    assert Executor.execute(codes)


def test_typecheck_int_NG(tc: TypeChecker) -> None:
    context: Context = Context({})
    codes = tc.typecheck('test', int, context=context)
    assert not Executor.execute(codes)


def test_typecheck_str_OK(tc: TypeChecker) -> None:
    context: Context = Context({})
    codes = tc.typecheck('test', str, context=context)
    assert Executor.execute(codes)


def test_typecheck_str_NG(tc: TypeChecker) -> None:
    context: Context = Context({})
    codes = tc.typecheck(42, str, context=context)
    assert not Executor.execute(codes)
