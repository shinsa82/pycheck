"""
testcases for parsing 'typespec's and AST (= type object used in PyCheck) generation.
"""
from logging import debug, info, warning
from pprint import pformat
from warnings import warn

from lark import Tree
from lark.exceptions import UnexpectedInput, UnexpectedToken
# needed for name resolution (= eval), so do not delete
from pandas import DataFrame
from pycheck.parser import gen_typespec, parse_typespec
from pycheck.type.util import pretty
from pytest import mark, raises

GEN_AST = True


def _show(s: str) -> None:
    """
    Common test utility.

    It parses given string and, if GEN_AST is true, it try to construct AST.
    """
    print('-- original --')
    print('(empty)' if s == '' else s)
    t: Tree = parse_typespec(s)
    print('')
    print('-- parsed tree --')
    print(t)
    # info('-- pprint --')
    # info("\n" + pformat(t))
    print('')
    print("-- pretty printed --\n" + t.pretty())
    # debug(t.data)
    # debug(t.children)
    if t.data == '_ambig':
        warn(
            'internal: parsing result is not unique! ask developers to update grammar.')
        return
    if GEN_AST:
        o = gen_typespec(t, text=s, globals_=globals() | locals())
        print(f'generated typespec obj = {pformat(o, sort_dicts=False)}')
        print(pretty(o))

def test_closure():
    "experiment on closure, for evaluation of types."
    assert 'DataFrame' in globals()
    assert not 'DataFrame' in locals()


@mark.xfail(raises=UnexpectedInput, reason='ill-formed typespecs', strict=True)
@mark.parametrize('typ', [
    '', '->', '-> int', 'list | x:int -> int | str'
])
def test_xfail(typ):
    "types that cannot be parsed."
    _show(typ)


@mark.parametrize('typ', ['int', '(int)', 'str', 'DataFrame'])
def test_base(typ):
    "types that can be parsed only with Python 3 grammar."
    _show(typ)


@mark.parametrize('typ', ['NoneType', 'None'])
def test_none(typ):
    """
    None-related types.

    "None" is parsed as 'base_none', but "NoneType" is parsed as 'base NoneType'.
    """
    _show(typ)


@mark.parametrize('typ', ['list[int]', 'list[dict[str, int]]'])
def test_generics(typ):
    "generic types."
    _show(typ)


@mark.parametrize('typ', [
    'y:int->int',
    'y:int->x:int->int',
    'y:int,x:int->int',
    '(y:int,x:int)->int',
    '()->int'
])
def test_func_simple(typ):
    "types that involve functions and are simple."
    _show(typ)


@mark.parametrize('typ', [
    '(x:int->int)',
    '(x:int)->y:int->int',
    'x:int|str,y:int->int',
    'x:(int|str),y:int->int',
    'x:(int)->y:int->int',
    'f:(x:int->int)->int',
    'x:int->(y:int->int)',
])
def test_func_type(typ):
    "types that involve functions."
    _show(typ)


@mark.parametrize('typ', [
    'x:int -> int | str',  # should be parsed as func-type from int to "int|str"
    'list | (x:int -> int) | str',
    'list | (x:int -> int | str)'
])
def test_func_sum(typ):
    "types mix of func and sum."
    _show(typ)


@mark.parametrize('typ', ['x:int->y:int->int', 'x:int->y:(z:int->int)->int'])
def test_parser_ambig(typ):
    "types that may introduce grammar ambiguity, which current implementation does not cause."
    _show(typ)


@mark.parametrize('typ', [
    '{x:int | lambda x: x > 0}',
    'l:{x:list[int] | lambda x: x > 0} -> str',
    'm:{f: x: int -> int | lambda x: x > 0} -> str',
    'm:{f: (x: int) -> int | lambda x: x > 0} -> s: str -> int',
    'm:{f: (x: int) -> int | lambda x: x > 0} -> (s: str) -> int',
    'k: {z: x: {y: int | lambda y: y>0} -> int | lambda x: x > z} -> str',
])
def test_reftypes(typ):
    "types that involve refinement types."
    _show(typ)


@mark.parametrize('typ', [
    'l:{x:list[int] | lambda x: x > 0} -> str',
    'l:{list[int] | lambda x: x > 0} -> str',
])
def test_varless_reftypes(typ):
    "refinement types without base variable."
    _show(typ)


@mark.parametrize('typ', ['int | str', 'int|str|tuple'])
def test_sum(typ):
    "sum types."
    _show(typ)


@mark.parametrize('typ', ['x: int -> y: { y:int | lambda x,y: y>x } -> {z:int | lambda z,x: z > 2*x}'])
def test_parser_practical(typ):
    "types that are practically used."
    _show(typ)
