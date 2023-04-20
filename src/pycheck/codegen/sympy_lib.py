"""
custom extension classes for SymPy.

It includes ListExpr, List, ListSymbol and other helper classes.
"""
from sympy import Add, S, Symbol
from sympy.core import Basic, sympify
from sympy.core.expr import Expr
from sympy.core.kind import BooleanKind, Kind, NumberKind
from sympy.core.symbol import Str
from sympy.core.sympify import converter


class _ListKind(Kind):
    "code reused from NumberKind."
    def __new__(cls):
        return super().__new__(cls)

    def __repr__(self):
        return "ListKind"


ListKind = _ListKind()


class ListExpr(Expr):
    "Superclass for list expressions."
    kind = ListKind


class ListSymbol(Expr):
    is_commutative = False
    is_symbol = True
    is_Symbol = True
    kind = ListKind

    def __new__(cls, name):
        if isinstance(name, str):
            name = Str(name)
        obj = Basic.__new__(cls, name)
        return obj

    def _sympystr(self, printer):
        "custom printer for str."
        return printer._print(Symbol(self.name))

    def _latex(self, printer):
        "custom printer for latex."
        return printer._print(Symbol(self.name))

    @property
    def name(self):
        "return symbol name."
        return self.args[0].name

    @property
    def free_symbols(self):
        return {self}

    def _eval_simplify(self, **kwargs):
        "needed?"
        return self


class List(Expr):
    "wrapper class for literal lists."

    def __new__(cls, *args, **kwargs):
        if kwargs.get('sympify', True):
            args = (sympify(arg) for arg in args)
        obj = Basic.__new__(cls, *args)
        return obj

    def __len__(self):
        return len(self.args)

    def _sympystr(self, printer):
        return printer._print(list(self.args))

    def _latex(self, printer):
        # print(f"_latex() called: {self}")
        return printer._print(list(self.args))


# Commented out: since this converter applies "all" computation within SymPy.
# This causes unwanted convertion to List.
# # register to converter
# converter[list] = lambda l: List(*l)


class Cons(ListExpr):
    "Cons class."
    def __new__(cls, a, l):
        a, l = list(map(sympify, [a, l]))
        # print(srepr(a), srepr(l))
        if isinstance(l, List):
            return List(a, *l.args)
        obj = Basic.__new__(cls, a, l)
        return obj

    def doit(self, deep=False, **hints):
        # TODO: implement when deep=True
        return List(self.args[0]) + self.args[1]


class IsNil(Expr):
    "class to check if it's nil."
    kind = BooleanKind

    def __new__(cls, l):
        l = sympify(l)
        # print(srepr(l))
        if isinstance(l, List):
            return sympify(len(l) == 0)
        elif isinstance(l, Cons):
            return S.false
        obj = Basic.__new__(cls, l)
        return obj


class Len(Expr):
    "class to express len(L)."
    kind = NumberKind
    is_integer = True
    is_nonnegative = True

    def __new__(cls, l):
        l = sympify(l)
        # print(srepr(l))
        if isinstance(l, List):
            return sympify(len(l.args))
        elif isinstance(l, Cons):
            return Add(1, Len(l.args[1]))
        obj = Basic.__new__(cls, l)
        return obj


class Exist(Expr):
    "class to express ∃x.P(x)."
    kind = BooleanKind

    def __new__(cls, var, expr):
        """
        constructor.

        Here `var` is a bound variable, and
        `expr` is a SymPy expression that may contain the `var`.
        """
        obj = Basic.__new__(cls, var, expr)
        return obj

    def __and__(self, other):
        return other

    def __rand__(self, other):
        return other

    def doit(self, deep=False, **hints):
        # TODO: implement simplification
        return S.true
