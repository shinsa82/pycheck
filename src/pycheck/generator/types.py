"""
Type hierarchy for generators.
"""
from dataclasses import dataclass
from typing import Any


class Type:
    """
    The top-level type. Every type is a subclass of the Type.
    """


class BaseType(Type):
    """
    Base types.
    """


class IntType(BaseType):
    """
    Integer type.
    """


class FloatType(BaseType):
    """
    Floating-point number type.
    """


class BoolType(BaseType):
    """
    Boolean type.
    """


class CharType(BaseType):
    """
    Character type.
    """


class DataFrameType(Type):
    """
    DataFrame type.
    """


class ListType:
    """
    List type. It holds a type of its element.
    """


class StringType(ListType):
    """
    String type. It is an alias of ListType[CharType].
    """


class ProdType(Type):
    """
    Dependent product type (x:T1) * T2.
    """


@dataclass
class RefType(Type):
    """
    Refinement type, { x: T1 | P }.
    """
    var: str = None  # base variable name
    typ: Type = None  # base type
    # refinement predicate. being generate code text, so a function returns a text
    # should be expected as value of this field.
    predicate: Any = None


class FuncType(Type):
    """
    Dependent function type, (x:T1) -> T2.
    """
