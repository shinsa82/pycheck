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


@mark.xfail
def test_func_annotated():
    "typecheck annotaed function."
    b: bool = typecheck(add_decorated)
    assert b

# common cases: non-annoted terms


@mark.xfail
def test_func_not_annotated():
    "typecheck non-annotaed function."
    b: bool = typecheck(add, '(y:int, x:int) -> int')
    assert b


@mark.xfail
def test_tuple_ref_not_annotated():
    "typecheck non-annotaed function."
    v: Tuple[int, int] = (3, 5)
    b: bool = typecheck(v, '(x:int, {y:int | y>x})')
    assert b
