"Types used in PyCheck."
from collections import OrderedDict
from dataclasses import dataclass
from inspect import Signature, signature
from typing import Any
from warnings import warn


@dataclass
class Type:
    type_name: str
    type_: Any
    text: str = None  # alias of type_name
    dirty: bool = False  # True if .text and .type_ do not match

    def __post_init__(self):
        self.text = self.type_name


@dataclass
class Base(Type):
    "Python base type like int or str."


@dataclass
class Generic(Type):
    "Generic type like 'list[str]'."


@dataclass
class Sum(Type):
    "Sum types like 'int | str'."
    choices: list[Any] = None


class ArgsType(metaclass=type):
    """Class for specifying arguments' types of a function."""

    def __init__(self, params=None, **kwargs):
        super().__init__()
        if params:  # see parser/__init__.py
            self.args_type = OrderedDict(params)
        else:
            # older init
            self.args_type = kwargs

    def __repr__(self):
        return f"ArgsType({self.args_type!r})"

    def __str__(self):
        return f"ArgsType({self.args_type})"

    def __rshift__(self, return_type):
        warn('">>" operator is no longer used.', DeprecationWarning)
        return FunctionType(self, return_type)

    def __eq__(self, other: "ArgsType") -> bool:
        return self.args_type == other.args_type

    def __iter__(self):
        "returns an iterator of [(variable name, its type)]."
        return iter(self.args_type.items())


@dataclass
class FunctionType(Type):
    # class FunctionType(Type, metaclass=type):
    """Class for specifying type of a function that can contains refinement types."""
    args_type: ArgsType = None
    return_type: Type = None
    args: ArgsType = None

    # def __init__(self, args_type: ArgsType, return_type, type_name=None, type_=None):
    #     self.raw_args_type = args_type

    #     self.args_type = args_type
    #     # self.args_type = args_type.args_type # commented out to integrate parser module

    #     self.return_type = return_type
    #     self.type_name = type_name  # see parser/__init__.py
    #     self.type_ = type_  # see parser/__init__.py
    def __post_init__(self):
        self.args = self.args_type

    def __str__(self):
        return f"FunctionType({self.args_type} -> {self.return_type})"


class SignatureFunctionType(FunctionType):
    """
    Function type that uses Signature as typespec.

    I forgot how to use this.
    """

    def __init__(self, signature: Signature) -> None:
        self.raw_args_type = signature
        self.args_type = {k: p.annotation for k,
                          p in signature.parameters.items()}
        self.return_type = signature.return_annotation


args = ArgsType


@dataclass
class RefinementType(Type):
    """
    Refinement types.

    TODO: Definition of Refinement class in core.py should be merged to this.
    """
    base_var: str = None
    base_type: Type = None
    predicate: Any = None
    signature: Signature = None  # signature of the predicate

    def __post_init__(self):
        super().__post_init__()
        if self.predicate:
            self.signature = signature(self.predicate)


__all__ = ['Type', 'Base', 'Generic', 'Sum', 'FunctionType', 'RefinementType']
