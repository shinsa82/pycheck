"""
custom extension classes for SymPy.

It includes ListExpr, List, ListSymbol and other helper classes.
"""
from logging import getLogger

from sympy import Add, S, Symbol, simplify
from sympy.core import Basic, Tuple, sympify
from sympy.core.containers import TupleKind
from sympy.core.expr import Expr
from sympy.core.kind import BooleanKind, Kind, NumberKind
from sympy.core.symbol import Str
from sympy.core.sympify import converter
from sympy.logic.boolalg import ITE, And, Boolean, Or, to_dnf

logger = getLogger(__name__)


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
    is_extended_real = False
    is_number = False

    kind = ListKind

    binary_symbols = set()

    def __new__(cls, name):
        if isinstance(name, str):
            name = Str(name)
        obj = Basic.__new__(cls, name)
        return obj

    def __getitem__(self, i):
        return GetItem(self, i)

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

    def __getitem__(self, i):
        return GetItem(self, i)

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


class IsNil(Expr, Boolean):
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

        Here `var` is a bound variable (not tuple), and
        `expr` is a SymPy expression that may contain the `var`.
        """
        expr = sympify(expr)
        obj = Expr.__new__(cls, sympify(var), expr)
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

    def _sub(self, expr):
        if expr.func == All:
            logger.info("DEBUG: Exist(All) to True")
            return S.true
        if expr.func == And or expr.func == Or:
            return expr.func(*[self._sub(arg) for arg in expr.args])
        return expr

    def _pullout(self, exist):
        "pull out free expression out of the Exist."
        var = exist.args[0]
        expr = exist.args[1]

        if expr.func == And:
            free_exprs = []
            bound_exprs = []
            # debug print
            logger.info("bound variable = %s", var)
            logger.info("expr (of %s) =", expr.func)
            for i, arg in enumerate(expr.args):
                logger.info("%d: %s", i, arg)
                logger.info(arg.free_symbols)
                if var in arg.free_symbols:
                    bound_exprs.append(simplify(arg))
                else:
                    free_exprs.append(simplify(arg))
            return And(*free_exprs, Exist(var, And(*bound_exprs)))

        return exist

    def _eval_simplify(self, **kwargs):
        "needed?"
        logger.info("simplifying Exist...")
        assert len(self.args) == 2
        var = self.args[0]
        expr = self.args[1]

        # debug print
        # logger.info("bound variable = %s", var)
        # logger.info("expr (of %s) =", expr.func)
        # for i, arg in enumerate(expr.args):
        #     logger.info("%d: %s", i, arg)
        #     logger.info(arg.free_symbols)

        if expr == S.true:  # (Exist x. True) -> True
            return S.true

        exist2 = Exist(var, self._sub(expr))
        return self._pullout(exist2)

        # if expr.func == All:  # TODO: (Exist x. All(...)) -> True
        #     logger.info("DEBUG: Exist(All) to True")
        #     return S.true
        # # (Exist x. And(...)) -> (Exist x. And'(...))
        # if expr.func == Or:
        #     return Or(*[Exist(var, arg) for arg in expr.args])
        #     # # analyze each phrases under And
        #     # new_args = []
        #     # free_expr = None
        #     # for arg in expr.args:
        #     #     if arg.func == All:
        #     #         logger.info("DEBUG: Exist(All) to True")
        #     #         new_args.append(S.true)
        #     #     else:
        #     #         new_args.append(arg)
        #     # return Exist(var, And(*new_args))
        # return self


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
        elif isinstance(t, List):
            if i < len(t.args):
                return t.args[i]
        elif isinstance(t, Cons):
            x = t.args[0]
            y = t.args[1]
            if i == 0:
                return x
            else:
                return GetItem(y, i-1)
        obj = Basic.__new__(cls, t, i)
        return obj

    def _sympystr(self, printer):
        return printer._print(self.args[0]) + "[" + printer._print(self.args[1]) + "]"


class IsSorted(Expr, Boolean):
    kind = BooleanKind

    def __new__(cls, l):
        l = sympify(l)
        if isinstance(l, list):
            return sympify(len(l) == 0)
        elif isinstance(l, List):
            ll = l.args
            return S(len(ll) == 0 or all(ll[i] <= ll[i+1] for i in range(len(ll)-1)))
        elif isinstance(l, Cons):
            y = l.args[0]
            z = l.args[1]
            return IsNil(z) | ((Len(z) >= 1) & (y < z[0]) & IsSorted(z))
            # return ITE(
            #     IsNil(z),
            #     S.true,
            #     (y < z[0]) & IsSorted(z)
            # )
        obj = Basic.__new__(cls, l)
        return obj
