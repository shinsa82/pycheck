"test of codegen, especially gen_gen()."
from logging import getLogger

from rich import print
from rich.markup import escape
from sympy import Dummy, Lambda, S, Symbol, Tuple, true

from pycheck import RefType
from pycheck.codegen.codegen_new import gen_inner
from pycheck.codegen.sympy_lib import IsSorted, ListSymbol
from pycheck.executor import PyCheckAssumeError, PyCheckFailError
from pycheck.random.random_generators import rand_bool, rand_int

from .utils import codegen_gen_and_exec as check
from .utils import true_func

logger = getLogger(__name__)

locals_ = {'rand_int': rand_int, 'rand_bool': rand_bool,
           'Lambda': Lambda,
           'Tuple': Tuple,
           'Symbol': Symbol,
           'true': true,
           'PyCheckAssumeError': PyCheckAssumeError,
           'PyCheckFailError': PyCheckFailError}


# def exec_code(code):
#     "subroutine for test."
#     # locals_ = {}
#     logger.info("executing code...")
#     exec(code.text, globals(), locals_)
#     for _ in range(10):
#         result = locals_[code.entry_point]()  # returns a generated value
#         logger.info("generated value = %s", result)


class TestBase:
    "test for base types and predicate function."

    def test_base0(self):
        "generates type 'int'."
        check('int', custom_tc=lambda x: isinstance(x, int))

    def test_base1(self):
        "simplest test"
        _z = Symbol('z')
        check('int', constraint=Lambda((_z,), 0 < _z))

    def test_base2(self):
        "simplest test"
        _z = Symbol('z')
        check('int', constraint=Lambda((_z,), _z >= 0))

    def test_base3(self):
        "simplest test"
        _z = Symbol('z')
        check("int", constraint=Lambda((_z,), _z < 4))

    def test_base4(self):
        "simplest test"
        _z = Symbol('z')
        check("int", constraint=Lambda((_z,), _z <= 4))

    def test_base5(self):
        "a case that requires simplification."
        _z = Symbol('z')
        check("int", constraint=Lambda((_z,),
                                       (0 < _z) & (3 < _z)))

    def test_base6(self):
        "a case that requires simplification."
        _z = Symbol('z')
        check("int", constraint=Lambda((_z,),
                                       (0 < _z) & (_z < 3)))

    def test_base7(self):
        "our tool works on polynomial constraints if it can be solved."
        _z = Symbol('z')
        check("int", constraint=Lambda((_z,), 2 * _z + 1 <= 4))

    def test_base8(self):
        "if it cannot be solved by SymPy, trial and error will be done."
        _z = Symbol('z')
        check("int", constraint=Lambda((_z,), _z ** 2 <= 9))

    def test_base9(self):
        "simplest test"
        _z = Symbol('z')
        _w = Symbol('w')
        check('int', constraint=Lambda((_z,), _w < _z), custom_env={_w: 10})

    def test_base10(self):
        "generates type 'bool'."
        check('bool', custom_tc=lambda x: isinstance(x, bool))


class TestRef:
    "generating refinement types."

    def test_ref0(self):
        "simplest test"
        reftype = RefType("{ y:int | y>0 }")
        check("{ y:int | y>0 }")

    def test_ref1(self):
        "simplest test"
        reftype = RefType("{x: { y:int | y>0 } | x>2}")
        check("{x: { y:int | y>0 } | x>2}")

    def test_ref2(self):
        """
        generates (initial) assume checking code
          x0 = rand_int(); assume(x0 > 0 and x0 < 5)
        then fused to
          x0 = rand_int(min=1, max=4)
        """
        reftype = RefType("{x: { y:int | y>0 } | x<5}")
        check("{x: { y:int | y>0 } | x<5}")

    def test_ref3(self):
        "case that has a free variable."
        # reftype = RefType("{ y:int | y>x }")
        check("{ y:int | y>x }", strict=False, custom_env={Symbol('x'): 10})


class TestProd:
    "generating product types."

    def test_prod0(self):
        "simplest test"
        check("x:int * int")

    def test_prod1(self):
        "simplest test"
        check("x:{w:int|w>20} * int")

    def test_prod2(self):
        "simplest test"
        check("x:int * {w:int|w>x}")

    def test_prod3(self):
        "refinement on prod"
        # TODO: rarely fails? and typechecking fails?
        check("{ x: (y:int * int) | x[0] > x[1] }")

    def test_prod4(self):
        "simplest test"
        check("x:int * {w:int| (x < w) & (w < x+5) }")


class TestFunc:
    "generating function types."

    def test_func0(self):
        check("x:int -> int", func=True)

    def test_func1(self):
        check("x:int -> { r:int | r > 20 }", func=True)

    def test_func2(self):
        check("x:int -> { r:int | r > x }", func=True)


class TestList:
    "generating list types."

    def test_list0(self):
        "simplest test"
        check("list[int]")

    def test_list1(self):
        "simplest test"
        check("list[{x:int|x>-5}]")

    def test_list2(self):
        "sorted list"
        check("{ l:list[int] | is_sorted(l) }", max_iter=20)

    def test_list3(self):
        "case when the list part has open variable(s)."
        check("x:int * list[{ y:int | y > x }]", max_iter=20)

    # def test_list2(self):
    #     "simplest test"
    #     reftype = parse_reftype("{l: list[int] | len(l)>0 }")
    #     # code, _ = gen_gen(reftype, lambda z: S.true, CodeGenContext())
    #     code, _ = gen_gen(reftype, S('lambda z: True'), CodeGenContext())

    #     exec_code(code)

    # def test_innter_gen(self):
    #     "test for inner generator (gen() function in the list generation)."
    #     reftype = parse_reftype("int")
    #     code, _ = gen_inner_gen(reftype, CodeGenContext())

    #     print(code.text)
    #     # not needed to execute


class TestGenInner:
    "test for the inner method of gen_list."

    def _check(self, typ, constraint):
        reftype = RefType(typ, strict=False)

        print(f"type = {escape(typ)}")
        print(f"type ast = {reftype.type_obj}")
        print(f"constraint = {constraint}")

    def test_positive(self):
        pass

    def test_issorted(self):
        typ = "list[int]"
        l = ListSymbol('l')
        constraint = Lambda((l,), IsSorted(l))
        self._check(typ, constraint)
