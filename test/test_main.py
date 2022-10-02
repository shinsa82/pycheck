"PyCheck e2e tests."
from typing import Tuple
from pycheck import reftype, typecheck
from pytest import mark

#
# sample inputs
#


def add(y: int, x: int) -> int:
    "sample undecorated function."
    return x + y


@reftype('(y:int, x:int) -> int')
def add_decorated(y: int, x: int) -> int:
    "sample decorated function."
    return x + y

#
# main tests
#

# special cases: annoted functions


def test_func_annotated():
    "typecheck annotaed function."
    b: bool = typecheck(add_decorated)
    assert b

# common cases: non-annoted terms


def test_func_not_annotated():
    "typecheck non-annotaed function."
    b: bool = typecheck(add, '(y:int, x:int) -> int')
    assert b


def test_base_types():
    "typecheck base."
    v: int = 13
    b: bool = typecheck(v, 'int')
    assert b


def test_prod_types():
    "typecheck product (triple)."
    v: tuple[int, int] = (11, 13, 15)
    b: bool = typecheck(v, 'x:int * y:int * int')
    assert b


def test_prod_ref_types():
    "typecheck product type with refinement."
    v: Tuple[int, int] = (3, 5)
    b: bool = typecheck(v, 'x:int * {y:int | y>x}')
    assert b


def test_ref_only_types():
    "typecheck refinement types."
    v: int = 5
    b: bool = typecheck(v, '{x:int | x>0}')
    assert b

#
# fail cases
#


def test_fail_ref_only_types():
    "typecheck refinement types."
    v: int = -1
    b: bool = typecheck(v, '{x:int | x>0}')
    assert not b
