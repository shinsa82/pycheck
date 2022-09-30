"test annotations by the reftype decorator."
from inspect import signature

from pycheck import get_reftype, has_reftype, reftype
from pycheck.reftype import RefType
from pytest import mark, raises


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


def test_spec_does_not_change_signature():
    "test if signature is not changed by annotation."
    assert signature(add) == signature(add_decorated)
    assert add(3, 4) == 7
    assert add_decorated(3, 4) == 7


def test_has_reftype():
    "test if has_reftye works."
    assert not has_reftype(add)
    assert has_reftype(add_decorated)


def test_get_reftype_OK():
    "test of get_reftype() when function is annotated."
    rt: RefType = get_reftype(add_decorated)
    assert isinstance(rt, RefType)
    assert rt.type == '(y:int, x:int) -> int'
    assert rt.ast is not None


def test_get_reftype_NG1():
    "test of get_reftype() when function is NOT annotated (case of function)."
    with raises(AttributeError, match="reftype is not assigned"):
        get_reftype(add)


def test_get_reftype_NG2():
    "test of get_reftype() when function is NOT annotated (case of builtin)."
    with raises(AttributeError, match="reftype is not assigned"):
        get_reftype(max)


def test_get_reftype_NG3():
    "test of get_reftype() when function is NOT annotated (case of class or others)."
    with raises(AttributeError, match="reftype is not assigned"):
        get_reftype(map)
