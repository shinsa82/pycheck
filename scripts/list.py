from sympy import Lambda

from pycheck import RefType
from pycheck.codegen import CodeGenContext
from pycheck.codegen.codegen_new import gen_inner
from pycheck.codegen.sympy_lib import IsSorted, ListSymbol

l = ListSymbol('l')
ff = gen_inner(RefType("list[int]").type_obj, Lambda(
    (l,), IsSorted(l)), context=CodeGenContext())
