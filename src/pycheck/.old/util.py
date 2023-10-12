"""
Utility functions.
"""
from logging import Logger, getLogger
from operator import attrgetter
from typing import Callable


def func_name(func: Callable) -> str:
    """
    Returns the name (or text representation) of the given function, which is 'func.__name__' or 'str(func)'.

    Args:
        func (Callable): target function.

    Returns:
        str: for named function, it's name. for unnamed ones, its text representation.
    """
    return getattr(func, "__name__", str(func))


def get_logger(mod_name: str) -> tuple[Logger, ...]:
    """
    Returns a tuple of loggers (debug, info, warning, error, exception)
    for the given module name (typically value of the '__name__').

    Args:
        mod_name (str): [description]

    Returns:
        tuple[Logger, ...]: [description]
    """
    return attrgetter('debug', 'info', 'warning', 'error', 'exception')(getLogger(mod_name))
