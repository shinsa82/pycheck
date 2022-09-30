"tests for parsing reftype."
from logging import getLogger

from lark import Tree
from pycheck.parsing import parse_reftype
from pytest import mark

logger = getLogger(__name__)


@mark.parametrize('type_', [
    "int",
    "bool",
    "char",
    "str",
    "float",
    "None"
])
def test_parse_base_type(type_):
    "parses base types."
    t: Tree = parse_reftype(type_)
    logger.info(t)
    logger.info("\n" + t.pretty())
    assert t.data == "base_type"


@mark.parametrize(
    'type_', [
        "list[int]",
        "list[list[char]]"
    ])
def test_parse_list_type(type_):
    "parses list types."
    t: Tree = parse_reftype(type_)
    logger.info(t)
    logger.info("\n" + t.pretty())
    assert t.data == "list_type"


@mark.parametrize(
    'type_', [
        "{ x:int | x > 0 }",
        "{ int | x > 0 }"
    ])
def test_parse_ref_type(type_):
    "parses refinement types."
    t: Tree = parse_reftype(type_)
    logger.info(t)
    logger.info("\n" + t.pretty())
    assert t.data == "ref_type"


@mark.parametrize(
    'type_', [
        "(x:int) -> int",
        "(x_1:int) -> int",
        "x:int -> int",
        "(x:int, y:int) -> int",
        "(x:int) -> (y:int) -> int"
    ])
def test_parse_func_type(type_):
    "parses base types."
    t: Tree = parse_reftype(type_)
    logger.info(t)
    logger.info("\n" + t.pretty())
    assert t.data == "func_type"


@mark.parametrize(
    'type_', [
        "x:int * int",
        "x:int * y:int * int",
        "x:int * y:int * { z:int | z >= x and z >= y }"
    ])
def test_parse_prod_type(type_):
    "parses product types."
    t: Tree = parse_reftype(type_)
    logger.info(t)
    logger.info("\n" + t.pretty())
    assert t.data == "prod_type"
