"tests for PycheckType."
from lark import Tree
from pytest import mark
from rich.pretty import pprint

from pycheck.parsing import parse_reftype
from pycheck.types import get_type


def _sub(type_str):
    tree: Tree = parse_reftype(type_str)
    print(tree.pretty())
    type_obj = get_type(tree)
    pprint(type_obj, indent_guides=False)
    return type_obj


@mark.parametrize('type_str', [
    "int",
    "bool",
])
def test_base_OK(type_str):
    "parses base types."
    type_obj = _sub(type_str)


@mark.xfail(raises=NotImplementedError)
@mark.parametrize('type_str', [
    "char",
    "str",
    "float",
    "NoneType"
])
def test_base_NG(type_str):
    "parses base types."
    type_obj = _sub(type_str)


@mark.parametrize(
    'type_str', [
        "x:int * bool",
        "(x:int) * bool",
        "x:int * (y:int * int)",
        "x:int * { y:int | y > x }",
    ])
def test_prod_OK(type_str):
    "parses product types."
    type_obj = _sub(type_str)


@mark.xfail(raises=NotImplementedError)
@mark.parametrize(
    'type_str', [
        "x:int * y:int * int",
        "x:int * y:int * { z:int | z >= x and z >= y }"
    ])
def test_prod_NG(type_str):
    "parses product types."
    type_obj = _sub(type_str)


@mark.parametrize(
    'type_str', [
        "{ x:int | x > 0 }",
        "{ x:list[int] | len(x) > 0 }",
    ])
def test_ref_OK(type_str):
    "parses refinement types."
    type_obj = _sub(type_str)


@mark.xfail(raises=NotImplementedError)
@mark.parametrize(
    'type_str', [
        # "x:" is missing.
        "{ int | x > 0 }"
    ])
def test_ref_NG1(type_str):
    "parses refinement types."
    type_obj = _sub(type_str)


@mark.xfail(raises=ValueError)
@mark.parametrize(
    'type_str', [
        # y's scope is closed within "{y: int | y>0}".
        "{ x: {y: int | y>0} | x > y }",
    ])
def test_ref_NG2(type_str):
    "parses refinement types."
    type_obj = _sub(type_str)


@mark.parametrize(
    'type_str', [
        "list[int]",
        "list[list[int]]",
        "list[{x:int | x>0}]",
        "list[ x:int * bool ]",
    ])
def test_list_OK(type_str):
    "parses product types."
    type_obj = _sub(type_str)


@mark.xfail(raises=NotImplementedError)
@mark.parametrize(
    'type_str', [
        "list[list[char]]"
    ])
def test_list_NG(type_str):
    "parses product types."
    type_obj = _sub(type_str)


@mark.parametrize(
    'type_str', [
        "(x:int) -> int",
        "(x_1:int) -> int",
        "x:int -> int",
        "(x:int) -> (y:int) -> int",
        "x:list[int] -> int",
        "x:list[int] -> (y:int * int)",
        # how to write refinement predicate is somehow special
        # you need to use "&" for "and", "|" for "or".
        # Inaddition, you need parentheses for each subterm.
        "x:list[int] -> (y:int * {z:int | (x>z) & (y>z)})",
    ])
def test_func_OK(type_str):
    "parses product types."
    type_obj = _sub(type_str)


@mark.xfail(raises=NotImplementedError)
@mark.parametrize(
    'type_str', [
        "( ) -> int",
        "(x:int, y:int) -> int",
    ])
def test_func_NG(type_str):
    "parses product types."
    type_obj = _sub(type_str)
