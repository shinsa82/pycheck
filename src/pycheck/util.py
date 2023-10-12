"""
Utility functions.
"""
from logging import Logger, getLogger
from operator import attrgetter
from typing import Callable
from sympy import Dummy, Lambda, S, Symbol, Tuple, true


def func_name(func: Callable) -> str:
    """
    Returns the name (or text representation) of the given function,
    which is 'func.__name__' or 'str(func)'.

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
    This is useful for developers since it makes shortcuts to each logging method.

    Args:
        mod_name (str): [description]

    Returns:
        tuple[Logger, ...]: [description]
    """
    return attrgetter('debug', 'info', 'warning', 'error', 'exception')(getLogger(mod_name))


def perf_ms(start: float, end: float, simple=False, divide: int = None):
    """
    return elapsed time in msec.

    By default it returns a string like '120.1 ms'.
    If `simple` is set to True, it returns a float number like 120.1.
    """
    duration = (end - start) * 1000.0
    if divide is not None:
        duration = duration / divide

    if simple:
        return duration
    else:
        return f"{duration} ms"


def true_func():
    "get new True constant function, 'lambda x: true', with a fresh variable."
    return Lambda((Dummy('x'),), S.true)
