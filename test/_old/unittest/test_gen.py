from collections.abc import Callable
from typing import Annotated

from pytest import mark

import pycheck.gen
from pycheck import Refinement
from pycheck.core import DataFrame, Series

xfail = mark.xfail
gen = pycheck.gen.gen


def gen_values(typ, context=None, f=None):
    print()
    for i in range(10):
        a = gen(typ, context)
        print(f'gen #{i+1}: {a}')
        if f:
            f(a)


def test_gen_int():
    gen_values(int)


@xfail
def test_gen_str():
    gen_values(str)


def test_gen_callable():
    def app(f):
        x = gen(int)
        print(f'  f({x}) = {f(x)}')
    gen_values(Callable[[int], int], app)


nat = Annotated[int, Refinement('x', lambda x: x >= 0)]


def test_gen_refinement():
    print('\n** genereates { x:int | x >= 0 }')
    gen_values(nat, context={})


def test_gen_list():
    print('\n** genereates list[int]')
    gen_values(list[int])


def test_gen_list2():
    print('\n** genereates list[{ x:int | x >= 0 }]')
    gen_values(list[nat], context={})


def test_gen_list3():
    print('\n** genereates list[{ y:int | y >= x }] where x=5')
    gen_values(list[Annotated[int, Refinement(
        'y', lambda x, y: y >= x)]], context={'x': 5})


def test_gen_series():
    print('\n** genereates Series[int]')
    gen_values(Series[int], context={})


def test_gen_df():
    gen_values(DataFrame[{'id': int, 'name': str}], context={})
