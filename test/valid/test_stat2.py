"""
stat exploration using pandas related code.
"""
from math import isclose, sqrt
from pprint import pformat, pprint

import pytest
from numpy.random import default_rng
from pandas import DataFrame, Series, set_option
from pycheck.config import Config
from pycheck.opcode import (  # used to parse the spec. do not delete.
    Evaluator, Result, Statistics)
from pycheck.parser import parse
from pycheck.spec import spec
from pycheck.typecheck import TypeChecker
from pycheck.typecheckers import set_defaults
from pycheck.util import get_logger

from .pandas_checkers import SeriesIntChecker
from .util import run

debug, info, warning, _, _ = get_logger(__name__)


@pytest.fixture
def tc() -> TypeChecker:
    "returns a TypeChecker with default checkers."
    return set_defaults(TypeChecker(config=Config())).register(SeriesIntChecker())


@pytest.fixture
def ev() -> Evaluator:
    "return an Evaluator of opcodes."
    return Evaluator()


def test_main():
    # debug('globals = ')
    # debug(pformat(globals()))
    assert SeriesIntChecker().can_handle(parse('Series', globals_=globals()))


@spec('n:{x:int|lambda x:x>0} -> {r:Series|lambda n,r: r.size==n}')
def series_func(n: int) -> Series:
    rng = default_rng()
    arr = rng.integers(low=-100, high=100, size=n, endpoint=True)
    return Series(arr)


def test_ret_series(tc: TypeChecker, ev: Evaluator):
    "tests a function that returns a Series."
    stat: Statistics = ev.evaluate(
        run(tc, series_func), config=Config(stat=True))
    assert stat.result == Result.OK

    show_stat(stat.detail)


@spec('l:Series -> {n: int | lambda l,n: l.size==n}')
def series_func2(l: Series) -> int:
    return l.size


def test_gen_series(tc: TypeChecker, ev: Evaluator):
    "tests a function that returns a Series."
    stat: Statistics = ev.evaluate(
        run(tc, series_func2), config=Config(stat=True))
    assert stat.result == Result.OK

    show_stat(stat.detail)


def show_stat(detail) -> None:
    "shows stat detail."
    print(pformat(detail))
    set_option('display.width', None)
    print()
    df = DataFrame.from_records(detail)
    # df['length'] = df['value'].map(lambda s: s.size)
    print(df)

    # df_true = df.query("satisfied == True")
    # df_false = df.query("satisfied == False")
    # print(df_true)
    # print()
    # print(df_true.describe())
    # print()
    # print(df_false)
    # print()
    # print(df_false.describe())


@spec('(x:{int|lambda x:x>0}, y:{int|lambda y:y>0},'
      'z:{int|lambda x,y,z:z>0 and x<y+z and y<z+x and z<x+y}) -> float')
def trig_area(x: int, y: int, z: int) -> float:
    s = (x + y + z) / 2
    return sqrt(s * (s - x) * (s - y) * (s - z))


def test_trig_area() -> None:
    assert isclose(trig_area(3, 4, 5), 6.0)


def test_bandit(tc: TypeChecker, ev: Evaluator):
    stat: Statistics = ev.evaluate(
        run(tc, trig_area), config=Config(stat=True, max_tries=10000))
    # assert stat.result == Result.OK

    # show_stat(stat.detail)
    # pprint(stat.detail)
    print()
    pos = list(filter(lambda d: d['addr'] ==
                      6 and d['satisfied'], stat.detail))
    print(f'-- positve instances ({len(pos)}) --')
    pprint(pos)
    print()
    neg = list(filter(lambda d: d['addr'] ==
               6 and not d['satisfied'], stat.detail))
    print(f'-- negative instances ({len(neg)}) --')
    pprint(neg)
