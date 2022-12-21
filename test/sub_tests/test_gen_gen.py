"test of codegen, especially gen_gen()."
from logging import getLogger

from sympy import Lambda, S, Symbol, Tuple, true

from pycheck.codegen import CodeGenContext
from pycheck.codegen.generators import gen_gen, gen_inner_gen
from pycheck.executor import PyCheckAssumeError, PyCheckFailError
from pycheck.parsing import parse_reftype
from pycheck.random.random_generators import rand_bool, rand_int

logger = getLogger(__name__)

locals_ = {'rand_int': rand_int, 'rand_bool': rand_bool,
           'Lambda': Lambda,
           'Tuple': Tuple,
           'Symbol': Symbol,
           'true': true,
           'PyCheckAssumeError': PyCheckAssumeError,
           'PyCheckFailError': PyCheckFailError}


def exec_code(code):
    # locals_ = {}
    logger.info("executing code...")
    exec(code.text, globals(), locals_)
    result = locals_[code.entry_point]()  # returns a generated value
    logger.info("done. result = %s", result)


def test_psi_0():
    "generates type 'int'."
    reftype = parse_reftype("int")
    code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())

    exec_code(code)


def test_psi_0a():
    "generates type 'int'. other version of psi."
    reftype = parse_reftype("int")
    code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

    exec_code(code)


def test_psi_1():
    "simplest test"
    reftype = parse_reftype("int")
    code, _ = gen_gen(reftype, lambda z: z > 0, CodeGenContext())

    exec_code(code)


def test_psi_2():
    "simplest test"
    reftype = parse_reftype("int")
    code, _ = gen_gen(reftype, lambda z: z >= 0, CodeGenContext())

    exec_code(code)


def test_psi_3():
    "simplest test"
    reftype = parse_reftype("int")
    code, _ = gen_gen(reftype, lambda z: 0 < z, CodeGenContext())

    exec_code(code)


def test_psi_4():
    "a case that requires simplification."
    reftype = parse_reftype("int")
    code, _ = gen_gen(reftype, lambda z: (0 < z) & (3 < z), CodeGenContext())

    exec_code(code)

#
# Refinement types
#


def test_ref_0():
    "simplest test"
    reftype = parse_reftype("{ y:int | y>0 }")
    code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())

    exec_code(code)


def test_ref_1():
    "simplest test"
    reftype = parse_reftype("{x: { y:int | y>0 } | x>2}")
    code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())

    exec_code(code)


def test_ref_2():
    "simplest test"
    reftype = parse_reftype("{x: { y:int | y>0 } | x<5}")
    code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())

    exec_code(code)

#
# List types
#


def test_list_0():
    "simplest test"
    reftype = parse_reftype("list[int]")
    # code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())
    code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

    exec_code(code)


def test_list_1():
    "simplest test"
    reftype = parse_reftype("{l: list[int] | len(l)>0 }")
    # code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())
    code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

    exec_code(code)


def test_innter_gen():
    "test for inner generator (gen() function in the list generation)."
    reftype = parse_reftype("int")
    code, _ = gen_inner_gen(reftype, CodeGenContext())

    print(code.text)
    # not needed to execute
