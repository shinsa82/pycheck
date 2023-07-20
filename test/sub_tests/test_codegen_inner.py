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


class TestGenInner:
    "test for the inner method of gen_list."

    def _check(self, typ, constraint):
        reftype = RefType(typ, strict=False)

        print(f"type = {escape(typ)}")
        print(f"type ast = {reftype.type_obj}")
        print(f"constraint = {constraint}")

        code = gen_inner(reftype.type_obj, constraint)
        print(code())

    def test_positive(self):
        typ = "list[{x:int | x>0}]"
        constraint = true_func()
        self._check(typ, constraint)

    def test_issorted(self):
        typ = "list[int]"
        l = ListSymbol('l')
        constraint = Lambda((l,), IsSorted(l))
        self._check(typ, constraint)
