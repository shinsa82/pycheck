"PyCheck e2e tests."
from datetime import datetime
from typing import Tuple

from pycheck import Result, reftype, typecheck
from pytest import mark

#
# sample inputs
#


def add(y: int, x: int) -> int:
    "sample undecorated function."
    return x + y


def inc(x: int) -> int:
    return x+1


def not_ident(x: int) -> int:
    return x + 10


@reftype('(y:int, x:int) -> int')
def add_decorated(y: int, x: int) -> int:
    "sample decorated function."
    return x + y


def max_(p: tuple[int, int]) -> int:
    return p[0] if p[0] >= p[1] else p[1]


def list_first(L: list[int]) -> int:
    return L[0]

#
# main tests
#

# special cases: annoted functions


def test_func_types_annotated():
    "typecheck annotaed function."
    b: bool = typecheck(add_decorated)
    assert b

# common cases: non-annoted terms


def test_func_types():
    "typecheck non-annotaed function."
    b: bool = typecheck(add, '(y:int, x:int) -> int')
    assert b


def test_func_1():
    "typecheck the simplest function."
    b: bool = typecheck(inc, '(x:int) -> int')
    assert b


def test_func_2():
    "typecheck the function that return type is refinement type."
    b: bool = typecheck(inc, '(x:int) -> {r:int|r>x}')
    assert b


def test_func_3():
    "typecheck the function that argument type is refinement type."
    b: bool = typecheck(inc, '(x:{y:int|y>0}) -> {r:int|r>x}')
    assert b


def test_func_4():
    """
    typecheck the function that may fail depends on random generation.

    This test fails at high probability.
    """
    r: Result = typecheck(not_ident, 'x:int -> {r:int|r>0}', detail=True)
    print(r)
    print(repr(r))
    b: bool = r.well_typed
    assert not b


def test_func_5():
    "typecheck the function that argument type is product type."
    start = datetime.now()
    b: bool = typecheck(
        max_, 'm:((n:int) * int) -> {r:int|r>=m[0] and r>=m[1]}')
    delta = datetime.now() - start
    print(delta.total_seconds())
    assert b


def test_func_6():
    "typecheck the function that argument type is product type and has refinement type."
    start = datetime.now()
    b: bool = typecheck(
        max_, 'h:( (i:int) * { j:int | i >= j } ) -> {r:int | r == h[0]}')
    delta = datetime.now() - start
    print(delta.total_seconds())
    assert b


def test_func_list():
    "typecheck the function with list generation."
    start = datetime.now()
    b: bool = typecheck(
        list_first, 'L: {ll: list[int] | len(ll) > 0 } -> int')
    delta = datetime.now() - start
    print(f"time elapsed: {delta.total_seconds()}s")
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


def test_list_only_types():
    "typecheck list."
    v: list[int] = [11, 13, 15]
    b: bool = typecheck(v, 'list[int]')
    assert b


def test_list_ref_types():
    "typecheck list type with refinement."
    v: list[int] = [11, 13, 15]
    b: bool = typecheck(v, 'list[{x:int|x>0}]')
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


def test_fail_list_ref_types():
    "typecheck list type with refinement."
    v: list[int] = [11, -13, 15]
    b: bool = typecheck(v, 'list[{x:int|x>0}]')
    assert not b
