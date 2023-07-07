"test of codegen, especially gen_typecheck()."
from logging import basicConfig, getLogger

from rich.logging import RichHandler

from pycheck import RefType
from pycheck.codegen import code_gen

from .utils import codegen_tc_and_exec as check

ENABLE_LOGGER: bool = False

if ENABLE_LOGGER:
    FORMAT = "%(message)s"
    basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

# pylint:disable=invalid-name
# pylint:disable=invalid-name

logger = getLogger(__name__)


class TestBase:
    "testcases for base types."

    def test_base0(self):
        "typechecks type 'int'."
        check("int", 3, is_typed=True)

    def test_base1(self):
        "typechecks type 'bool'."
        check("bool", True, is_typed=True)

    def test_base2(self):
        "this does not simple typechecking. So it passes."
        check("bool", 3, is_typed=True)


class TestRef:
    "testcases for refinement types."

    def test_ref0(self):
        "typechecks refinement type."
        check("{x:int | x>0}", 5)

    def test_ref1x(self):
        "typechecks refinement type."
        check("{x:int | x>0}", -1, is_typed=False)

    def test_ref2(self):
        "typechecks nested refinement type."
        check("{x: { y:int | y>0 } | x<5}", 3)

    def test_ref3x(self):
        "typechecks nested refinement type."
        check("{x: { y:int | y>0 } | x<5}", -1, is_typed=False)

    def test_ref4x(self):
        "typechecks nested refinement type."
        check("{x: { y:int | y>0 } | x<5}", 6, is_typed=False)

    def test_ref5(self):
        "typechecks nested refinement type (simplified case)."
        check("{x: { y:int | y>0 } | x>5}", 7)


class TestList:
    "testcases for list types."

    def test_list0(self):
        "typechecks list type."
        check("list[int]", [2, 0, -1])

    def test_list1(self):
        "typechecks list+ref type."
        check("list[{ x: int | x>0 }]", [2, 1, 1])

    def test_list2x(self):
        "typechecks list+ref type."
        check("list[{ x: int | x>0 }]", [2, 0, -1], is_typed=False)

    def test_list3(self):
        "typechecks list length."
        check("{ l:list[int] | len(l) > 1 }", [2, 0, -1])

    def test_list4x(self):
        "typechecks list length."
        check("{ l:list[int] | len(l) > 1 }", [2], is_typed=False)

    def test_list5(self):
        "typechecks list length."
        check("{ l:list[int] | is_sorted(l) }", [1, 2, 3])

    def test_list6x(self):
        "typechecks list length."
        check("{ l:list[int] | is_sorted(l) }", [3, 2, 3],  is_typed=False)


class TestFunc:
    "typechecks function types. see test_codegen_gen.py for further random generation."

    def test_func0(self):
        "typechecks function types (delta). Thus it is always typed."
        def v(x):
            return x + 1
        check("x:int -> int", v, max_iter=30)

    def test_func1(self):
        "typechecks function types (beta). It generates input and check output."
        def v(x):
            return x + 1
        check("x:int -> int", v, max_iter=30)

    def test_func2(self):
        "typechecks function types (beta). It generates input and check output."
        def v(x):
            return x + 1
        check("x:{y:int|y>0} -> int", v, max_iter=30)

    def test_func3x(self):
        "typechecks function types (beta). It generates input and check output."
        def v(x):
            return x**2 - 15**2
        check("x:{y:int|y>0} -> {z:int|z>0}", v, is_typed=False, max_iter=30)

    def test_func4(self):
        "typechecks function types (beta). It generates input and check output."
        # this test FAILS due to gen_base().
        def v(x):
            return x + 1
        check("x:int -> {r:int|r>x}", v, max_iter=30)

    def test_func5x(self):
        "typechecks function types (beta). It generates input and check output."
        # this test FAILS due to gen_base().
        def v(x):
            return abs(x) - 1
        check("x:int -> {r:int|r<x}", v, is_typed=False, max_iter=30)


class TestProd:
    "typechecks product types."

    def test_prod1(self):
        "typechecks product type."
        check("x:int * int", (2, 3), is_typed=True)

    def test_prod2(self):
        "typechecks product type."
        check("x:int * {y:int | y>x}", (2, 3), is_typed=True)

    def test_prod3x(self):
        "typechecks product type."
        check("x:int * {y:int | y>x}", (5, 3), is_typed=False)

    def test_prod4(self):
        "typechecks product type."
        check("list[x:int * {y:int | x < y}]",
              [(1, 2), (2, 3), (3, 4)], is_typed=True)

    def test_prod5x(self):
        "typechecks product type."
        check("list[x:int * {y:int | x < y}]",
              [(1, 2), (2, 3), (3, 3)], is_typed=False)
