"test of QE (quantifier elimination)"
from sympy import (ITE, And, Dummy, Function, GreaterThan, Integer, Lambda,
                   LessThan, Rational, S, StrictGreaterThan, StrictLessThan,
                   Symbol, ceiling, floor, simplify, srepr)

from pycheck.codegen import qe
from pycheck.codegen.sympy_lib import (All, Cons, Exist, IsSorted, Len, List,
                                       ListSymbol, Map, TupleSymbol)


def test_qe1():
    "Exist(z4, All(Map(Lambda(_x, True), z4)) & (IsNil(z4) | (IsSorted(z4) & (Len(z4) >= 1) & (y3 < z4[0]))))"
    expr = ...
    qe(expr)
