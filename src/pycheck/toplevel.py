"""Module implementing top-level function, check()"""

from inspect import Signature, signature
from logging import getLogger
from operator import attrgetter
from typing import Any, Callable

from .config import Config, Context
from .spec import FunctionType, typespec
from .typecheck import TypeChecker
from .typecheckers import set_defaults

debug, info = attrgetter('debug', 'info')(getLogger(__name__))


def check(func: Any, config: Config = None) -> bool:
    """
    Top-level typecheck routine.

    It gets the type of the given function and pass them to typeckeck() func.
    """
    print(f'typechecking function {getattr(func, "__name__", str(func))}...')
    info(f'typechecking function {getattr(func, "__name__", str(func))}...')

    config = config or Config()
    info(f"with configuration {config}")

    # if isinstance(func, Testable):
    #     debug('getting signature...')
    #     sig: Signature = signature(func)
    #     info(f'signature = {sig}')
    #     typed = typecheck(func, signature(func), max_iter=max_iter)
    # else:
    #     raise TypeError(
    #         'PyCheck cannot typecheck non-functional types nor lambda functions')

    # get function signature
    func_type: FunctionType = typespec(func)

    # and typecheck
    tc = set_defaults(TypeChecker(config=config))
    well_typed = tc.typecheck(v=func, t=func_type, context=Context({}))

    if well_typed:
        # print(f'\nPASS (passed {max_iter} tests.)')
        print(f'PASS')
    else:
        # print('\nFAIL (falsyfiable after XXX tests)')
        print('FAIL')

    return well_typed


__all__ = ['check']
