"""
Tests if type normalization works.
"""
from inspect import signature
from typing import Any

import pytest
from pytest import mark
from pycheck.parser import parse
from pycheck.type import FunctionType, RefinementType
from pycheck.type.normalization import fusion_predicates, normalize, project, complete
from pycheck.type.util import pretty
from pycheck.util import get_logger

debug, info, _, _, _ = get_logger(__name__)


@mark.parametrize('spec', [
    'l:{x:list[int] | lambda x: len(x) > 0} -> str',
    'l:{list[int] | lambda l: len(l) > 0} -> str',
])
def test_varless(spec):
    print()
    print('-- spec --')
    print(spec)
    type_ = parse(spec)
    print('')
    print('-- before normalize --')
    print(type_)
    print(pretty(type_))
    print('-- completed --')
    type_ = complete(type_)
    # print(type_)
    print(pretty(type_))
    # ntype = normalize(type_)
    # print('')
    # print('-- after normalize --')
    # print(ntype)
    # print('')
    # print('-- pretty print --')
    # print(pretty(ntype))


def test_nested_ref():
    typ: FunctionType = normalize(parse(
        "a:int, b: { x: { y: int | lambda a, y: y<10 } | lambda a, x: x>0 } -> int"))
    print(pretty(typ))
    for v, t in typ.args:
        print(v, t)


@pytest.mark.parametrize('spec', [
    'int',
    'int|str|bool',
    'int|(str|bool)',
    'list[int]',
    '{x:int|lambda x: x>0}',
    'str | {x:{y:int|lambda y:y<10}|lambda x: x>0}',
    '{x:{y:int|lambda y:y<10}|lambda x: x>0}',
    'x:int -> int',
    'x:int -> (int|str)',
    '(x:int, y:{z:str|lambda x,z: len(z)>=x}) -> int',
    'a:int -> {x:{y:int|lambda y:y<10}|lambda x: x>0}',
    'z: {x:{y:int|lambda y:y<10}|lambda x: x>0} -> int',
])
def test_normalize(spec):
    print()
    print('-- spec --')
    print(spec)
    type_ = parse(spec)
    print('')
    print('-- before normalize --')
    print(type_)
    ntype = normalize(type_)
    print('')
    print('-- after normalize --')
    print(ntype)
    print('')
    print('-- pretty print --')
    print(pretty(ntype))


def test_project():
    kwargs = {'a': 1, 'b': 2, 'c': 3, 'x': 9}
    p = project(kwargs, {'a', 'c', 'x'})
    assert p == {'a': 1, 'c': 3, 'x': 9}


def test_predicate_fusion2():
    typ: RefinementType = normalize(
        parse('{x:{y:int|lambda y:y<10}|lambda x: x>0}'))
    print(pretty(typ))
    f = typ.predicate
    assert all([f(x=i) == (not (i == 0 or i == 10)) for i in range(11)])


def test_predicate_fusion():
    """
    tests predicate fusion that is used to normalize nested refinement types.
    """
    # Assume that context before f and g is [a, b, c]
    # and that f's base variable is x, g's one is y.
    # we assume x and y are surely contained in their argument lists.
    f = lambda a, c, x: a < x or c < x  # f uses a, c and x
    # g uses b, c and y, where y and x are the same.
    g = lambda b, c, y: b < y < c

    h = fusion_predicates(f, 'x', g, 'y')
    kwargs = {'a': 1, 'b': 2, 'c': 3, 'x': 9}
    assert not h(**kwargs)
    assert signature(h).parameters.keys() == {'a', 'b', 'c', 'x'}


# def test_gensig():
#     sig = Signature()
#     print(sig)

#     sig = Signature(return_annotation=int)
#     print(sig)

#     sig = Signature(parameters=[Parameter(
#         'x', kind=Parameter.POSITIONAL_OR_KEYWORD)])
#     print(sig)

#     sig = Signature(parameters=[
#         Parameter('x', kind=Parameter.POSITIONAL_OR_KEYWORD, default=3)
#     ])
#     print(sig)

#     sig = Signature(parameters=[
#         Parameter('x', kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
#     ])
#     print(sig)


# def test_signature_injection():
#     f = lambda a, b: a + b
#     g = lambda **kwargs: 1
#     print(signature(f))
#     print(signature(g))
#     g.__signature__ = signature(f)
#     print(signature(g))
#     g(2, 3)
