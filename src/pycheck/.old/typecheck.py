"""typecheck routine for each type."""
from abc import abstractmethod
from functools import cache
from inspect import Signature
from logging import getLogger
from math import exp
from operator import attrgetter
from random import getrandbits
from typing import (Annotated, Any, Callable, Iterable, Optional, Union,
                    get_args, get_origin)

from more_itertools import first_true

from .config import Config, Context
from .core import PyCheckAssertionError, Testable
from .gen import gen
from .opcode import Assign, OpCode, OpCodes
from .spec import FunctionType, SignatureFunctionType, typespec
from .type import Type
from .type.normalization import normalize

debug, info, error = attrgetter('debug', 'info', 'error')(getLogger(__name__))


class TypeCheckerImpl:
    """
    Implementation class of type checker for each type.

    Each TypeCheckerImpl sublass should implement three methods: 
    - can_handle()
    - typecheck_codes()
    - gen()
    - typecheck() // deprecated?
    """

    def _can_handle(self, t: Type) -> Any:
        "Returns 'self' if this typechecker can handle given type. Returns 'None' otherwise."
        if self.can_handle(t):
            return self
        else:
            return None

    @abstractmethod
    def can_handle(self, t: Type) -> bool:
        "Subclasses must implement this. It should return 'True' if this typechecker can handle given type. Should return 'False' otherwise."
        pass

    @abstractmethod
    def typecheck_codes(self, v: Any, t: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        "Returns op-codes for typechecking a term 'v' with type 't'."
        pass

    @abstractmethod
    def gen(self, to_name: str, type_: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        "Returns op-codes for generating a value of given type."
        pass

    @abstractmethod
    def typecheck(self, v: Any, t: Type, context: Context, manager: 'TypeChecker') -> bool:
        pass


class TypeChecker:
    """
    A manager of typechecker.

    Typecheckes for each type can be registered to this class.
    """

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.checkers: Iterable[TypeCheckerImpl] = []
        self.seed = config.seed or getrandbits(config.seed_nbits)
        self.index = 0

    def name(self, v: str) -> str:
        "returns variable name with index number to avoid conflict."
        name = f"{v}_{self.index}"
        self.index += 1
        return name

    def register(self, tc: TypeCheckerImpl) -> TypeCheckerImpl:
        self.checkers.append(tc)
        return self

    def _get_typechecker(self, t: 'Type') -> Optional[TypeCheckerImpl]:
        return first_true(self.checkers, pred=lambda tc: tc._can_handle(t))

    def typecheck(self, v: str, t: 'Type', context: Context) -> bool:
        """
        Typechecking main routine. It checks if term v (= variable string) can have type t.

        context contains variable context for dependent types.
        config contains config variables.
        """
        info(f'typecheck:')
        info(f'  term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'  context = {context}')

        debug(f'  getting typechecker for type {t}...')
        tc: Optional[TypeCheckerImpl] = self._get_typechecker(t)
        if not tc:
            error(f'No type checker for type {t} was found')
            raise ValueError(f'No type checker for type {t} was found')
        debug(f'type checker obtained: {tc}')
        # res = tc.typecheck(v, t, context=context, manager=self)
        opcodes = tc.typecheck_codes(v, t, context=context, manager=self)
        info(f'{opcodes=}')
        return opcodes

    def gen(self, to_name, type_: Type, context: Context) -> Iterable[OpCode]:
        tc = self._get_typechecker(type_)
        if not tc:
            error(f'No generator for type {type_} was found')
            raise ValueError(f'No generator for type {type_} was found')
        return tc.gen(to_name, type_=type_, context=context, manager=self)

    def renum(self, opcodes: OpCodes) -> OpCodes:
        "assigns addresses (= line numbers) to opcodes."
        for l, o in enumerate(opcodes):
            o.addr = l
        return opcodes

    def typecheck0(self, v: Any, t: Type = None) -> OpCodes:
        """
        (Temporary) top-level typecheck method. Name to be fixed.
        """
        if t is None:
            info('getting typespec from attached typespec')
            t = typespec(v)
        assert t is not None

        info('')
        info(f'-- typecheck (top-level) --')
        info(f'  term = {getattr(v, "__name__", str(v))}')
        info(f'  type = {t}')
        info(f"  seed = {self.seed} ({hex(self.seed)})")
        info(f'  config = {self.config}')

        initial_var = self.name('v')
        initial_code = [Assign(to=initial_var, exp=v)]
        opcodes = self.typecheck(initial_var, t, context=Context({}))

        res: OpCodes = self.renum(initial_code + opcodes)
        info(f'{res=}')
        return res


# def typecheck(v: Testable, t: Type, context: Context, config: Config) -> bool:
#     """
#     Checks if a term v is of type t.
#     """
#     info(f'typecheck: term = {getattr(v, "__name__", str(v))}, type = {t}')
#     info(f'context = {context}')
#     assert isinstance(t, Type), f'type {t} is unsupported or invalid'
#     if t is int:
#         res = isinstance(v, int)
#         info(f'typed? = {res}')
#         return res
#     if t is str:
#         res = isinstance(v, str)
#         info(f'typed? = {res}')
#         return res
#     if t is bool:
#         res = isinstance(v, bool)
#         info(f'typed? = {res}')
#         return res
#     elif isinstance(t, Signature):  # top-level function
#         try:
#             f: Callable = v
#             sig: Signature = t
#             passed = 1
#             while passed <= max_iter:
#                 print('.', end='')
#                 params = gen(sig)
#                 # debug(f'generated values = {params}')
#                 info('applying function...')
#                 res = f(**params)
#                 info(f'function application result = {res}')
#                 if not typecheck(res, sig.return_annotation, context=params):
#                     raise PyCheckAssertionError(
#                         f'type {sig.return_annotation} expected')
#                 info(f'test {passed=}')
#                 passed += 1
#             info(f'typed? = True (passed {max_iter} tests.)')
#             return True
#         except PyCheckAssertionError:
#             info(f'typed? = False')
#             # print_exc(file=sys.stdout)
#             info(f'Falsifying example: {params}')
#             return False
#     elif get_origin(t) is Annotated:
#         base, refinement = get_args(t)
#         var = refinement.var
#         predicate = refinement.predicate
#         debug('doing base type check')
#         if not typecheck(v, base, context=context):
#             return False
#         tmp_context = context | {var: v}
#         debug(f'context for refinement check: {tmp_context}')
#         ref_check_res = predicate(**tmp_context)
#         debug(f'refinement predicate satisfiled? = {ref_check_res}')
#         return ref_check_res
#     else:
#         raise NotImplementedError(
#             f'typechecking for type {t} has not been implemented yet')


__all__ = ["typecheck", "TypeChecker", "TypeCheckerImpl"]
