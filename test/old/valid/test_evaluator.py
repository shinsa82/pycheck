"""
test for executing the results of test_codeden.py.
"""
from logging import getLogger
from pprint import pprint

import pytest
from more_itertools import is_sorted
from pycheck import spec
from pycheck.config import Config
from pycheck.opcode import Evaluator, Result
from pycheck.typecheck import TypeChecker
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


class TestSimple:
    @staticmethod
    @spec('(x:int,y:int)->int')
    def add(x: int, y: int) -> int:
        "sample func 1"
        return x + y

    def test_add(self, tc: TypeChecker, ev: Evaluator) -> None:
        codes = run(tc, TestSimple.add)
        ev.evaluate(codes)


@spec('l: { m:list[int] | lambda m: len(m)>0 and is_sorted(m) } -> int')
def pick_min(l: list[int]) -> int:
    "test target func."
    return l[0]


class TestRefTypes:
    @staticmethod
    @spec('(x:{i:int | lambda i: i>0}, y:{j:int | lambda x,j: x>=j})->{z:int| lambda z,**kwargs: z>=0}')
    def dec_reftype(x: int, y: int) -> int:
        "dec() annotated with (over-specified) refinement types."
        return x - y

    @staticmethod
    @spec('(l: list[int], n: {i: int | lambda l, i: 0 <= i < len(l)}) -> {r: int | lambda l,n,r: r==l[n]}')
    def nth(l: list[int], n: int) -> int:
        return l[n]

    def test_dec(self, tc: TypeChecker, ev: Evaluator) -> None:
        codes = run(tc, TestRefTypes.dec_reftype)
        ev.evaluate(codes, config=Config(max_iteration=100))

    def test_sorted(self, tc: TypeChecker, ev: Evaluator) -> None:
        "test refined list type generation."
        codes = run(tc, pick_min)
        ev.evaluate(codes, config=Config(max_iteration=100))

    def test_nth(self, tc: TypeChecker, ev: Evaluator) -> None:
        "test simple reftype function."
        codes = run(tc, TestRefTypes.nth)
        assert ev.evaluate(codes)


class TestList:
    @staticmethod
    @spec('l: list[int] -> {r:list[int] | lambda r: is_sorted(r)}')
    def my_sort(l: list[int]) -> list[int]:
        "test target"
        return []

    def test_list_func(self, tc: TypeChecker, ev: Evaluator) -> None:
        codes = run(tc, TestList.my_sort)
        assert ev.evaluate(codes).result == Result.OK


class TestBad:
    @staticmethod
    @spec('(x:int, y:{j:int | lambda x: x*x==-1})->int')
    def f(x: int, y: int) -> int:
        "ill-specified function. specification will never be satisfied"
        return x + y

    @staticmethod
    @spec('(x: int, y: int) -> {r: int | lambda r: r>=0}')
    def g(x: int, y: int) -> int:
        "ill-typed function."
        return x - y

    def test_timeout(self, tc: TypeChecker, ev: Evaluator) -> None:
        codes = run(tc, TestBad.f)
        assert ev.evaluate(codes, config=Config(
            max_tries=100)).result == Result.TIMEOUT

    def test_fail(self, tc: TypeChecker, ev: Evaluator) -> None:
        codes = run(tc, TestBad.g)
        assert ev.evaluate(codes, config=Config(
            max_iteration=10)).result == Result.FAIL
