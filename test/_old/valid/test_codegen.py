"""
test of typecheck_codes() in typechechecker impls.
"""
from typing import Callable

import pytest
from more_itertools import is_sorted
from pycheck import spec
from pycheck.config import Config
from pycheck.examples.sato import double_, fsum, main
from pycheck.opcode import Assume_, IsIns
from pycheck.typecheck import TypeChecker
from pycheck.typecheckers import ListIntTypeChecker, set_defaults
from pycheck.util import get_logger
from pytest import mark

from .util import p, run

debug, info, _, _, _ = get_logger(__name__)


@pytest.fixture
def tc() -> TypeChecker:
    "returns a TypeChecker with default checkers"
    return set_defaults(TypeChecker(config=Config()))


class TestSimple:
    @staticmethod
    @spec('(y:int, x:int)->int')
    def add(y: int, x: int) -> int:
        "sample func 1"
        return x + y

    @staticmethod
    @spec('y:int->x:int->int')
    def add_curry(y: int) -> Callable[[int], int]:
        "sample func 2"
        return (lambda x: x + y)

    def test_add(self):
        "test add() itself"
        assert TestSimple.add(3, 5) == 8

    def test_add_curry(self):
        "test add_curry() itself"
        assert (TestSimple.add_curry(3))(5) == 8

    def test_typecheck_int(self, tc: TypeChecker) -> None:
        codes = run(tc, 42, t=p('int'))
        assert len(codes) == 2
        assert isinstance(
            codes[1], IsIns) and codes[1].v == 'v_0' and codes[1].type_ == int

    def test_typecheck_str(self, tc: TypeChecker) -> None:
        codes = run(tc, 'test', t=p('str'))
        assert len(codes) == 2
        assert isinstance(
            codes[1], IsIns) and codes[1].v == 'v_0' and codes[1].type_ == str

    def test_typecheck_add(self, tc: TypeChecker) -> None:
        codes = run(tc, TestSimple.add)
        # assert len(codes) == 1
        # assert isinstance(
        #     codes[0], IsIns) and codes[0].v == 'test' and codes[0].t == str

    def test_typecheck_add_curry(self, tc: TypeChecker) -> None:
        codes = run(tc, TestSimple.add_curry)


class TestSatoExamples:
    def test_double(self, tc: TypeChecker) -> None:
        run(tc, double_)

    def test_main(self, tc: TypeChecker) -> None:
        run(tc, main)

    def test_fsum(self, tc: TypeChecker) -> None:
        run(tc, fsum)


class Samples:
    "sample functions."
    @staticmethod
    @spec('x: {y:int | lambda y: y>0} -> int')
    def simple(x: int) -> int:
        return x * x


class TestRefTypes:
    @staticmethod
    @spec('(x:{i:int | lambda i:i>0}, y:{j:int | lambda x,j:x>=j})->{z:int| lambda z: z>=0}')
    def dec_reftype(x: int, y: int) -> int:
        "def() annotated with (over-specified) refinement types."
        return x - y

    def test_simple_reftype(self, tc: TypeChecker) -> None:
        assert run(tc, Samples.simple)

    def test_dec(self, tc: TypeChecker) -> None:
        codes = run(tc, TestRefTypes.dec_reftype)

        assert len(codes) == 10
        code = codes[2]
        assert isinstance(code, Assume_)
        assert code.bind == ('i', 'i')
        assert callable(code.pred)
        assert code.pred(i=1)
        assert not code.pred(i=-1)

        code: Assume_ = codes[5]
        assert code.pred(x=1, j=1)
        assert code.pred(**{'x': 1, 'j': 1})
        assert not code.pred(x=1, j=5)
        assert not code.pred(**{'x': 1, 'j': 5})

    def test_typecheck_list_int(self) -> None:
        assert ListIntTypeChecker.is_list_int([1, 2, 3])
        assert not ListIntTypeChecker.is_list_int([1, 'test', 3])

    def test_is_sorted(self) -> None:
        assert is_sorted([-3, 0, 1, 2, 4])
        assert not is_sorted([3, 0, 1, 2, 4])

    def test_sorted(self, tc: TypeChecker) -> None:
        "test refined list type generation."

        @spec('l: { m:list[int] | lambda m: len(m)>0 and is_sorted(m) } -> int')
        def pick_min(l: list[int]) -> int:
            "test target func."
            return l[0]

        codes = run(tc, pick_min)
        assert len(codes) > 0

    @staticmethod
    @spec('x: {y: {z:int | lambda z: z>0} | lambda y: y<=5}-> int')
    def nested(x: int) -> int:
        return x - 1

    def test_nested(self, tc: TypeChecker) -> None:
        codes = run(tc, TestRefTypes.nested)
        assert len(codes) > 0


def func_varless(l: list[int]):
    return str(l[0])


class TestVarless():
    @mark.parametrize('spec', [
        'l:{x:list[int] | lambda x: len(x) > 0} -> str',
        'l:{list[int] | lambda l: len(l) > 0} -> str',
    ])
    def test_varless(self, tc: TypeChecker, spec) -> None:
        codes = run(tc, f=func_varless, t=spec)
        assert len(codes) > 0
