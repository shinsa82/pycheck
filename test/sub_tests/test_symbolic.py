"test symbolic computation."
from dataclasses import dataclass
from typing import Any

from lark import Tree
from pycheck import Result, reftype, typecheck
from pycheck.codegen import gen_gen, CodeGenContext
from pycheck.parsing import parse_reftype
from pytest import mark, raises


@dataclass
class Var:
    name: str


@dataclass
class Exp:
    term: Any
    var: str = None

    def __add__(self, other):
        if isinstance(other, Exp):
            self.term = ['+', self.term, other.term]  # symbolic + symbolic
            return self
        else:
            self.term = ['+', self.term, other]  # symbolic + value
            return self

    def __radd__(self, left):
        if isinstance(left, Exp):
            self.term = ['+', left.term, self.term]   # symbolic + symbolic
            return self
        else:
            self.term = ['+', left, self.term]  # symbolic + value
            return self


def test_symbolic_1():
    "addition of values."
    e = (lambda x, y: x + y)(1, 2)
    assert e == 3


def test_symbolic_2():
    "addition of a value and a variable."
    e = (lambda x, y: x + y)(Exp(Var('x')), 2)
    print(e)
    assert e == Exp(term=['+', Var(name='x'), 2])


def test_symbolic_3():
    "addition of a value and a variable."
    e = (lambda x, y: x + y)(2, Exp(Var('y')))
    print(e)
    assert e == Exp(term=['+', 2, Var(name='y')])


def test_symbolic_4():
    "addition of a value and a variable."
    e = (lambda x, y: x + y)(Exp(Var('x')), Exp(Var('y')))
    print(e)
    assert e == Exp(term=['+', 2, Var(name='y')])


def _f(x: int) -> int:
    if not x > 0:
        raise ValueError
    return x - 1


def test_typecheck():
    "typecheck the function with list generation."
    b: bool = typecheck(
        _f, "x:{ xx:int | xx > 0 } -> { r:int | r >= 0 }")
    assert b


def test_gen():
    "test code generator for alpha() directly."
    t: Tree = parse_reftype("{ xx:int | xx > 0 }")
    code = gen_gen(t, lambda z: True, CodeGenContext())
    print(code)
