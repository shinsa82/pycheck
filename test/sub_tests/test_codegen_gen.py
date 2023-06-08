"test of codegen, especially gen_gen()."
from logging import getLogger

from sympy import Dummy, Lambda, S, Symbol, Tuple, true

from pycheck import RefType
from pycheck.codegen import CodeGenContext, code_gen
from pycheck.codegen.codegen import gen_gen, gen_inner_gen
from pycheck.executor import PyCheckAssumeError, PyCheckFailError
from pycheck.parsing import parse_reftype
from pycheck.random.random_generators import rand_bool, rand_int

from .utils import exec_gen_code, true_func

logger = getLogger(__name__)

locals_ = {'rand_int': rand_int, 'rand_bool': rand_bool,
           'Lambda': Lambda,
           'Tuple': Tuple,
           'Symbol': Symbol,
           'true': true,
           'PyCheckAssumeError': PyCheckAssumeError,
           'PyCheckFailError': PyCheckFailError}


def exec_code(code):
    "subroutine for test."
    # locals_ = {}
    logger.info("executing code...")
    exec(code.text, globals(), locals_)
    for _ in range(10):
        result = locals_[code.entry_point]()  # returns a generated value
        logger.info("generated value = %s", result)


class TestBase:
    "test for base types and predicate function."

    def test_base0(self):
        "generates type 'int'."
        reftype = RefType('int')
        code = code_gen(reftype, mode="gen", constraint=true_func())

        exec_gen_code(code)

    def test_base1(self):
        "simplest test"
        reftype = RefType('int')
        _z = Symbol('z')
        code = code_gen(reftype, mode="gen", constraint=Lambda((_z,), 0 < _z))

        exec_gen_code(code)

    def test_psi2(self):
        "simplest test"
        reftype = RefType("int")
        _z = Symbol('z')
        code = code_gen(reftype, mode="gen", constraint=Lambda((_z,), _z >= 0))

        exec_gen_code(code)

    def test_psi3(self):
        "simplest test"
        reftype = RefType("int")
        _z = Symbol('z')
        code = code_gen(reftype, mode="gen", constraint=Lambda((_z,), _z < 4))

        exec_gen_code(code)

    def test_psi4(self):
        "simplest test"
        reftype = RefType("int")
        _z = Symbol('z')
        code = code_gen(reftype, mode="gen", constraint=Lambda((_z,), _z <= 4))

        exec_gen_code(code)

    def test_psi5(self):
        "a case that requires simplification."
        reftype = RefType("int")
        _z = Symbol('z')
        code = code_gen(reftype, mode="gen", constraint=Lambda((_z,),
                                                               (0 < _z) & (3 < _z)))

        exec_gen_code(code)

    def test_psi6(self):
        "a case that requires simplification."
        reftype = RefType("int")
        _z = Symbol('z')
        code = code_gen(reftype, mode="gen", constraint=Lambda((_z,),
                                                               (0 < _z) & (_z < 3)))

        exec_gen_code(code)


class TestRef:
    "generating refinement types."

    def test_ref0(self):
        "simplest test"
        reftype = RefType("{ y:int | y>0 }")
        code = code_gen(reftype, mode='gen', constraint=true_func())

        exec_gen_code(code)

    def test_ref1(self):
        "simplest test"
        reftype = RefType("{x: { y:int | y>0 } | x>2}")
        code = code_gen(reftype, mode='gen', constraint=true_func())

        exec_gen_code(code)

    def test_ref_2(self):
        """
        generates (initial) assume checking code
          x0 = rand_int(); assume(x0 > 0 and x0 < 5)
        then fused to
          x0 = rand_int(min=1, max=4)
        """
        reftype = RefType("{x: { y:int | y>0 } | x<5}")
        code = code_gen(reftype, mode='gen', constraint=true_func())

        exec_gen_code(code)


class TestProd:
    "generating product types."

    def test_prod0(self):
        "simplest test"
        reftype = RefType("x:int * int")
        code = code_gen(reftype, mode='gen', constraint=true_func())

        exec_gen_code(code)

    def test_prod1(self):
        "simplest test"
        reftype = RefType("x:{w:int|w>0} * int")
        code = code_gen(reftype, mode='gen', constraint=true_func())

        exec_gen_code(code)

    def test_prod2(self):
        "simplest test"
        reftype = RefType("x:int * {w:int|w>x}")
        code = code_gen(reftype, mode='gen', constraint=true_func())

        exec_gen_code(code)

    def test_prod3x(self):
        "refinement on prod"
        reftype = RefType("{ x: (y:int * int) | x[0] > x[1] }")
        code = code_gen(reftype, mode='gen', constraint=true_func())

        exec_gen_code(code)


class TestList:
    "generating list types."

    def test_list0(self):
        "simplest test"
        reftype = parse_reftype("list[int]")
        # code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())
        code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

        exec_code(code)

    def test_list1(self):
        "simplest test"
        reftype = parse_reftype("{l: list[int] | len(l)>0 }")
        # code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())
        code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

        exec_code(code)

    def test_innter_gen(self):
        "test for inner generator (gen() function in the list generation)."
        reftype = parse_reftype("int")
        code, _ = gen_inner_gen(reftype, CodeGenContext())

        print(code.text)
        # not needed to execute
