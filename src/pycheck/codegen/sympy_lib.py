"""
custom extension classes for SymPy.

It includes ListExpr, List, ListSymbol and other helper classes.
"""
from sympy import Add, S, Symbol
from sympy.core import Basic, Tuple, sympify
from sympy.core.containers import TupleKind
from sympy.core.expr import Expr
from sympy.core.kind import BooleanKind, Kind, NumberKind
from sympy.core.symbol import Str
from sympy.core.sympify import converter
from sympy.logic.boolalg import And, Boolean, Or


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
    is_commutative = False


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
    is_commutative = False

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
    is_commutative = False

    def __new__(cls, a, l):
        a, l = list(map(sympify, [a, l]))
        # print(srepr(a), srepr(l))
        if isinstance(l, List):
            return List(a, *l.args)
        if isinstance(l, list):
            return List(a, *l)
        obj = Basic.__new__(cls, a, l)
        return obj

    def doit(self, deep=False, **hints):
        # TODO: implement when deep=True
        self.args[0].doit()
        self.args[1].doit()
        if isinstance(self.args[1], List):
            return List(self.args[0], *self.args[1].args)
        return self


class IsNil(Expr):
    "class to check if it's nil."
    kind = BooleanKind

    def __new__(cls, l):
        l = sympify(l)
        # print(srepr(l))
        if isinstance(l, list):
            return sympify(len(l) == 0)
        elif isinstance(l, List):
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
        if isinstance(l, list):
            return sympify(len(l))
        if isinstance(l, List):
            return sympify(len(l.args))
        elif isinstance(l, Cons):
            return Add(1, Len(l.args[1]))
        obj = Basic.__new__(cls, l)
        return obj


class Map(Expr):
    "class to express map(L)."
    kind = ListKind
    is_integer = False

    def __new__(cls, f, l):
        l = sympify(l)
        # print(srepr(l))
        if isinstance(l, list):
            return List(*map(f, l))
        if isinstance(l, List):
            return List(*map(f, l.args))
        elif isinstance(l, Cons):
            return Add(1, Len(l.args[1]))
        obj = Basic.__new__(cls, f, l)
        return obj


class All(Expr, Boolean):
    "class to express all(L)."
    kind = ListKind
    is_integer = False

    def __new__(cls, l):
        l = sympify(l)
        if isinstance(l, list):
            return S(all(l))
        if isinstance(l, List):
            return S(all(l.args))
        obj = Basic.__new__(cls, l)
        return obj


class Exist(Expr, Boolean):
    "class to express ∃x.P(x)."
    kind = BooleanKind

    def __new__(cls, var, expr):
        """
        constructor.

        Here `var` is a bound variable, and
        `expr` is a SymPy expression that may contain the `var`.
        """
        obj = Expr.__new__(cls, sympify(var), sympify(expr))
        return obj

    @property
    def bound_symbols(self):
        return (self.args[0],)

    @property
    def free_symbols(self):
        return self.args[1].free_symbols - set([self.args[0]])

    # def __and__(self, other):
    #     if other == S.true:
    #         return self
    #     if other == S.false:
    #         return S.false
    #     return And(self, other)
    #     # return None

    # def __or__(self, other):
    #     if other == S.true:
    #         return S.true
    #     if other == S.false:
    #         return self
    #     return Or(self, other)

    # # def __rand__(self, other):
    # #     return other

    # def doit(self, deep=False, **hints):
    #     # TODO: implement simplification
    #     return S.true

    def _eval_simplify(self, **kwargs):
        "needed?"
        if self.args[1] == S.true:
            return S.true
        return self

class TupleSymbol(Expr):
    is_commutative = False
    is_symbol = True
    is_Symbol = True
    kind = TupleKind()

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

    def __getitem__(self, i):
        return GetItem(self, i)

    def __add__(self, other):
        # does not work?
        return NotImplemented


class GetItem(Expr):
    "class for item access of a tuple."
    def __new__(cls, t, i):
        t = sympify(t)
        i = sympify(i)
        if isinstance(t, Tuple):
            return t[i]
        obj = Basic.__new__(cls, t, i)
        return obj
