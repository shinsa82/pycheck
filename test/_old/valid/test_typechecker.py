"""
tests for typechecker manager and implementations.
"""
import pytest
from pycheck import Config, TypeChecker, TypeCheckerImpl
from pycheck.parser import parse
from pycheck.type import Base
from pycheck.typecheckers import IntTypeChecker, set_defaults
from pycheck.util import get_logger

info, _, _, _, _ = get_logger(__name__)


@pytest.fixture
def tc() -> TypeChecker:
    "fixture for a TypeChecker with a default Config."
    return TypeChecker(config=Config())


@pytest.fixture
def int_type() -> Base:
    return Base(type_name='int', type_=int)


@pytest.fixture
def str_type() -> Base:
    return Base(type_name='str', type_=str)


class TestCanHandle:
    """
    tests can_handle of each typechecker.

    It tests both .can_handle() and ._can_handle().
    """

    def test_can_handle(self, int_type: Base, str_type: Base):
        "test can_handle impl. (of int typechecker)"
        tc_int: TypeCheckerImpl = IntTypeChecker()
        assert tc_int.can_handle(int_type)
        assert not tc_int.can_handle(str_type)

    def test_underscore_can_handle(self, int_type: Base, str_type: Base):
        "test _can_handle (of int typechecker)"
        tc_int: TypeCheckerImpl = IntTypeChecker()
        assert tc_int._can_handle(int_type) is tc_int
        assert not tc_int._can_handle(str_type)


class TestRegister:
    "tests register and get_typechecker."

    def test_register0(self, tc: TypeChecker, int_type: Base):
        "test register and get_typechecker"
        assert tc._get_typechecker(int_type) is None

    def test_register1(self, tc: TypeChecker, int_type: Base):
        "can find typechecker for int type."
        tc_int: TypeCheckerImpl = IntTypeChecker()
        tc.register(tc_int)
        assert tc._get_typechecker(int_type) is tc_int

    def test_register2(self, tc: TypeChecker, str_type: Base):
        "cannot find typecher for str with only int typechecker registered."
        tc_int: TypeCheckerImpl = IntTypeChecker()
        tc.register(tc_int)
        assert tc._get_typechecker(str_type) is None

    def test_register3(self, tc: TypeChecker):
        "can find typechecker for sum type."
        set_defaults(tc)
        t = parse('int|str')
        info(t)
        assert tc._get_typechecker(t) is not None
