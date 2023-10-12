"""
Genrator implementations.
"""
from functools import singledispatch
from typing import Any, Callable, TypeAlias

from .types import BaseType, BoolType, CharType, FloatType, IntType, RefType

Code: TypeAlias = str


@singledispatch
def sigma_base(typ, name: str = "f") -> Code:
    """
    sigma function for base types.
    """
    raise NotImplementedError(
        f"sigma_base() not implemented for this arg: {typ}")


@sigma_base.register
def _(_: IntType, name: str = "f") -> Code:
    # isinstance(x, int) does not work as expected: since Bool <: Int.
    # return lambda x: isinstance(x, int) and x is not True and x is not False
    return "lambda x: isinstance(x, int) and x is not True and x is not False"


@sigma_base.register
def _(_: BoolType, name: str = "f") -> Code:
    return "lambda x: isinstance(x, bool)"


@sigma_base.register
def _(_: FloatType, name: str = "f") -> Code:
    return "lambda x: isinstance(x, float)"


@sigma_base.register
def _(_: CharType, name: str = "f") -> Code:
    return "lambda x: isinstance(x, str) and len(x) == 1"

#
# sigma() main function
#


@singledispatch
def sigma(typ, name: str = "f") -> Code:
    """
    sigma function in my paper.

    sigma(T) returns a program "text" that defines a function that implements σ(T)
    as an anonymous function.
    ~~name of the function is given by a parameter "name".~~ <- Now no "name" is needed.
    """
    raise NotImplementedError(f"sigma() not implemented for this arg: {typ}")


@sigma.register
def _(typ: BaseType, name: str = "f") -> Code:
    return sigma_base(typ)


@sigma.register
def _(typ: RefType, name: str = "f") -> Code:
    sigma_t = sigma(typ.typ)  # get sigma(base type)
    return f"lambda x: ({sigma_t})(x) and {typ.predicate('x')}"
