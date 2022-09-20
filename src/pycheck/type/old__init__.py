"""
PyCheck-specific types for expressing (dependent and) refinement types.
"""
from logging import getLogger
from typing import TYPE_CHECKING, Any, Callable, Iterable, TypeVar

from wrapt import decorator

info = getLogger(__name__).info


class RefinementType(metaclass=type):
    """
    Refinement types.

    TODO: Definition of Refinement class in core.py should be merged to this.
    """

    def __init__(self, base: type, var: str, predicate):
        "base: base type, var: variable name, predicate: predicate function"
        self.base = base
        self.var = var
        self.predicate = predicate


class Function:
    """
    Function types.
    """

    def __init__(self, args, returns):
        self.arg_types = args
        self.return_type = returns


class ArgsType(metaclass=type):
    def __init__(self, **kwargs: type) -> None:
        super().__init__()
        self.args_type = kwargs

    def __str__(self) -> str:
        return f"ArgsType({self.args_type})"

    def __rshift__(self, return_type) -> 'FunctionType':
        return FunctionType(self, return_type)


class FunctionType(metaclass=type):
    def __init__(self, args_type: ArgsType, return_type: type):
        self.args_type = args_type
        self.return_type = return_type

    def __str__(self) -> str:
        return f"FunctionType({self.args_type} -> {self.return_type})"


F = TypeVar('F', bound=Callable[..., Any])


def spec(type: FunctionType, check_argtype: bool = False) -> Callable[[F], F]:
    """decorator that specifies function sigunature of the decorated using refinement types"""
    info("spec (= type) of the function:")
    info(type)
    info(f"type check arguments when invoked? = {check_argtype}")

    @decorator
    def wrapper(wrapped, instance, args, kwargs):
        info("in the wrapper. show patched attributes...")
        info(f"{wrapped._type=}")
        info(f"{wrapped._check_argtype=}")
        if wrapped._check_argtype:
            info("typechecking arguments...")
        return wrapped(*args, **kwargs)

    def wrapping(wrapped):
        info(f"monkeypatching function {wrapped}")
        wrapped._type = type
        wrapped._check_argtype = check_argtype
        f = wrapper(wrapped)
        return f

    return wrapping
