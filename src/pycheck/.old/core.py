"""
Definitions of core classes and functions.
"""
from collections.abc import Callable
from inspect import Signature
from logging import getLogger
from operator import attrgetter
from types import FunctionType
from typing import Annotated, Any, Generic, TypeVar, get_origin

from .type import RefinementType as RefT

debug, info = attrgetter('debug', 'info')(getLogger(__name__))


class PyCheckAssertionError(AssertionError):
    pass


class TestableMeta(type):
    def __instancecheck__(self, other: Any) -> bool:
        # debug(other)
        # user-defined function, unless it's a lambda
        return isinstance(other, FunctionType) and \
            other.__name__ != '<lambda>'


class Testable(metaclass=TestableMeta):
    pass


T = TypeVar('T')


class Series(Generic[T]):
    "ad-hoc datatype for Series."
    pass

class DataFrame:
    "ad-hoc datatype for DataFrame."
    def __class_getitem__(cls, key):
        return f"{cls.__name__}[{key}]"


class TypeMeta(type):
    def __instancecheck__(self, instance: Any) -> bool:
        return \
            instance is int or \
            instance is str or \
            instance is bool or \
            isinstance(instance, Signature) or \
            isinstance(instance, RefT) or \
            get_origin(instance) in [Annotated, Callable, list, Series, DataFrame]


class Type(metaclass=TypeMeta):
    pass


class Refinement:
    def __init__(self, var, predicate):
        "var: variable name, predicate: predicate function"
        self.var = var
        self.predicate = predicate
