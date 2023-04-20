"test of codegen, especially gen_typecheck()."
from logging import getLogger

from pycheck import RefType
from pycheck.codegen import code_gen

from .utils import exec_code

# FORMAT = "%(message)s"
# basicConfig(
#     level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
# )

# pylint:disable=invalid-name

logger = getLogger(__name__)

# locals_ = {'rand_int': rand_int, 'rand_bool': rand_bool,
#            'Lambda': Lambda,
#            'Tuple': Tuple,
#            'Symbol': Symbol,
#            'true': true,
#            'PyCheckAssumeError': PyCheckAssumeError,
#            'PyCheckFailError': PyCheckFailError}

# the latest tests


class TestBase:
    "testcases for base types."

    def test_base0(self):
        "typechecks type 'int'."
        reftype = RefType("int")
        code = code_gen(3, reftype)

        exec_code(code, 3, is_typed=True)

    def test_base1(self):
        "typechecks type 'bool'."
        reftype = RefType("bool")
        v: bool = True
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)


class TestRef:
    "testcases for refinement types."

    def test_ref0(self):
        "typechecks refinement type."
        reftype = RefType("{x:int | x>0}")
        v: int = 5
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_ref1x(self):
        "typechecks refinement type."
        reftype = RefType("{x:int | x>0}")
        v: int = -1
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=False)

    def test_ref2(self):
        "typechecks nested refinement type."
        reftype = RefType("{x: { y:int | y>0 } | x<5}")
        v = 3
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_ref3x(self):
        "typechecks nested refinement type."
        reftype = RefType("{x: { y:int | y>0 } | x<5}")
        v = -1
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=False)

    def test_ref4x(self):
        "typechecks nested refinement type."
        reftype = RefType("{x: { y:int | y>0 } | x<5}")
        v = 6
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=False)


class TestList:
    "testcases for list types."

    def test_list1(self):
        "typechecks list type."
        reftype = RefType("list[int]")
        v: list[int] = [2, 0, -1]
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_list2(self):
        "typechecks list+ref type."
        reftype = RefType("list[{x: int | x>0 }]")
        v: list[int] = [2, 1, 1]
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_list3x(self):
        "typechecks list+ref type."
        reftype = RefType("list[{x: int | x>0 }]")
        v: list[int] = [2, 0, -1]
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=False)

    def test_list4(self):
        "typechecks list type."
        reftype = RefType("{ l:list[int] | len(l) > 1 }")
        v: list[int] = [2, 0, -1]
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)


class TestFunc:
    "typechecks function types. see test_codegen_gen.py for further random generation."

    def test_func1(self):
        "typechecks function types (delta). Thus it is always typed."
        reftype = RefType("x:int -> int")

        def v(x):
            return x + 1
        code = code_gen(v, reftype, is_delta=True)

        exec_code(code, v, is_typed=True)

    def test_func2(self):
        "typechecks function types (beta). It generates input and check output."
        reftype = RefType("x:int -> int")

        def v(x):
            return x + 1
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_func3(self):
        "typechecks function types (beta). It generates input and check output."
        reftype = RefType("x:{y:int|y>0} -> int")

        def v(x):
            return x + 1
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_func4(self):
        "typechecks function types (beta). It generates input and check output."
        reftype = RefType("x:int -> {r:int|r>x}")

        def v(x):
            return x + 1
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)


class TestProd:
    "typechecks product types."
    # @mark.skipif(True, reason="not refactored yet")

    def test_prod1(self):
        "typechecks product type."
        reftype = RefType("x:int * int")
        v: int = (2, 3)
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_prod2(self):
        "typechecks product type."
        reftype = RefType("x:int * {y:int | y>x}")
        v: int = (2, 3)
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=True)

    def test_prod3x(self):
        "typechecks product type."
        reftype = RefType("x:int * {y:int | y>x}")
        v: int = (5, 3)
        code = code_gen(v, reftype)

        exec_code(code, v, is_typed=False)

# # older version


# def test_psi_0a():
#     "generates type 'int'. other version of psi."
#     reftype = parse_reftype("int")
#     code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

#     exec_code(code)


# def test_psi_1():
#     "simplest test"
#     reftype = parse_reftype("int")
#     code, _ = gen_gen(reftype, lambda z: z > 0, CodeGenContext())

#     exec_code(code)


# def test_psi_2():
#     "simplest test"
#     reftype = parse_reftype("int")
#     code, _ = gen_gen(reftype, lambda z: z >= 0, CodeGenContext())

#     exec_code(code)


# def test_psi_3():
#     "simplest test"
#     reftype = parse_reftype("int")
#     code, _ = gen_gen(reftype, lambda z: 0 < z, CodeGenContext())

#     exec_code(code)


# def test_psi_4():
#     "a case that requires simplification."
#     reftype = parse_reftype("int")
#     code, _ = gen_gen(reftype, lambda z: (0 < z) & (3 < z), CodeGenContext())

#     exec_code(code)

# #
# # List types
# #


# def test_list_0():
#     "simplest test"
#     reftype = parse_reftype("list[int]")
#     # code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())
#     code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

#     exec_code(code)


# def test_list_1():
#     "simplest test"
#     reftype = parse_reftype("{l: list[int] | len(l)>0 }")
#     # code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())
#     code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

#     exec_code(code)


# def test_innter_gen():
#     "test for inner generator (gen() function in the list generation)."
#     reftype = parse_reftype("int")
#     code, _ = gen_inner_gen(reftype, CodeGenContext())

#     print(code.text)
#     # not needed to execute
