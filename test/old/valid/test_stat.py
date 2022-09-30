from itertools import groupby
from operator import attrgetter, itemgetter
from random import normalvariate
from typing import Any, Iterable, NewType

import pandas as pd
import pytest
from more_itertools import is_sorted
from pandas import DataFrame
from pycheck import spec
from pycheck.config import Config, Context
from pycheck.opcode import Evaluator, Gen, IsIns, OpCode, Result, Statistics
from pycheck.type import Base, Generic, Type
from pycheck.typecheck import TypeChecker, TypeCheckerImpl
from pycheck.typecheckers import set_defaults
from pycheck.util import get_logger

from .util import run

debug, info, _, _, _ = get_logger(__name__)


@pytest.fixture
def tc() -> TypeChecker:
    "returns a TypeChecker with default checkers."
    return set_defaults(TypeChecker(config=Config()))


@pytest.fixture
def ev() -> Evaluator:
    "return an Evaluator of opcodes."
    return Evaluator()


def test_stat():
    stat = Statistics()
    assert isinstance(stat.detail, list)


@spec('l: { m:list[int] | lambda m: len(m)>0 and is_sorted(m) } -> int')
def pick_min(l: list[int]) -> int:
    "test target func."
    return l[0]


list_int = NewType('list_int', list[int])


@spec('l: { m:list_int | lambda m: len(m)>0 and is_sorted(m) } -> int')
def pick_min2(l: list[int]) -> int:
    "test target func."
    return l[0]


pd.set_option('display.width', None)


class ListIntCustomTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, Base) and t.type_ == list_int

    @staticmethod
    def is_list_int(l) -> bool:
        return all(map(lambda e: isinstance(e, int), l))

    def typecheck_codes(self, v: Any, t: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        return [IsIns(v=v, type_=None, func=ListIntCustomTypeChecker.is_list_int)]

    @staticmethod
    def gen_list():
        "generate a random int number."
        len = abs(int(normalvariate(0, 20)))
        generated = sorted([int(normalvariate(0, 20)) for _ in range(len)])
        debug(f'rand_list: {generated=}')
        return generated

    def gen(self, to_name: str, type_: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        return [Gen(var=to_name, type_=type_, impl=ListIntCustomTypeChecker.gen_list)]


class TestRefTypes:
    def show_stat(self, detail) -> None:
        print()
        df = DataFrame.from_records(detail)
        df['length'] = df['value'].map(len)
        print(df)

        df_true = df.query("satisfied == True")
        df_false = df.query("satisfied == False")
        print(df_true)
        print()
        print(df_true.describe())
        print()
        print(df_false)
        print()
        print(df_false.describe())

    def test_sorted(self, tc: TypeChecker, ev: Evaluator) -> None:
        "test refined list type generation."
        codes = run(tc, pick_min)
        stat: Statistics = ev.evaluate(codes, config=Config(stat=True))
        assert stat.result == Result.OK

        self.show_stat(stat.detail)

    def test_sorted2(self, tc: TypeChecker, ev: Evaluator) -> None:
        "test refined list type generation."
        tc.register(ListIntCustomTypeChecker())
        codes = run(tc, pick_min2)
        stat: Statistics = ev.evaluate(codes, config=Config(stat=True))
        assert stat.result == Result.OK

        self.show_stat(stat.detail)
