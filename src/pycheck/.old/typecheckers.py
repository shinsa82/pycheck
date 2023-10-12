"""
Typechecker implementations for each type.
"""
from logging import getLogger
from operator import attrgetter
from pprint import pformat
from random import normalvariate
from typing import Any, Iterable, Union, get_origin
from warnings import warn

from more_itertools import flatten

from .config import Context
from .opcode import TC_, Apply, Assert_, Assume_, Gen, IsIns, Move, OpCode
from .type import Base, FunctionType, Generic, RefinementType, Sum, Type
from .typecheck import TypeChecker, TypeCheckerImpl

debug, info, warning, error = attrgetter(
    'debug', 'info', 'warning', 'error')(getLogger(__name__))


class IntTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, Base) and t.type_ == int

    def typecheck(self, v: Any, t: 'Type', context: Context, manager: TypeChecker) -> bool:
        info(f'typecheck: term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'context = {context}')
        info(f'config = {manager.config}')
        assert t == int
        res = isinstance(v, int)
        info(f'typed? = {res}')
        return res

    def typecheck_codes(self, v: Any, t: 'Type', context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        info('-' * 10 + ' ' + self.__class__.__name__ + ' ' + '-' * 10)
        info(f'typecheck_codes:')
        info(f'  term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'  context = {context}')
        info(f'  config = {manager.config}')
        assert isinstance(t, Base) and t.type_ == int
        return [IsIns(v=v, type_=int)]

    @staticmethod
    def gen_int():
        "generate a random int number."
        generated = int(normalvariate(0, 20))
        info(f'rand_int: {generated=}')
        return generated

    def gen(self, to_name: str, type_: Type, context: Context, manager: TypeChecker) -> Iterable[OpCode]:
        return [Gen(var=to_name, type_=type_, impl=IntTypeChecker.gen_int)]


class FloatTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, Base) and t.type_ == float

    def typecheck_codes(self, v: Any, t: 'Type', context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        info('-' * 10 + ' ' + self.__class__.__name__ + ' ' + '-' * 10)
        info(f'typecheck_codes:')
        info(f'  term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'  context = {context}')
        info(f'  config = {manager.config}')
        assert isinstance(t, Base) and t.type_ == float
        return [IsIns(v=v, type_=float)]

    @staticmethod
    def gen_float():
        "generate a random float number."
        generated = normalvariate(0, 20)
        info(f'rand_float: {generated=}')
        return generated

    def gen(self, to_name: str, type_: Type, context: Context, manager: TypeChecker) -> Iterable[OpCode]:
        return [Gen(var=to_name, type_=type_, impl=FloatTypeChecker.gen_float)]


class StrTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, Base) and t.type_ == str

    def typecheck(self, v: Any, t: 'Type', context: Context, manager: TypeChecker) -> bool:
        info(f'typecheck:')
        info(f'term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'context = {context}')
        assert t == str
        res = isinstance(v, str)
        info(f'typed? = {res}')
        return res

    def typecheck_codes(self, v: Any, t: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        info('-' * 10 + ' ' + self.__class__.__name__ + ' ' + '-' * 10)
        info(f'typecheck_codes:')
        info(f'  term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'  context = {context}')
        info(f'  config = {manager.config}')
        assert isinstance(t, Base) and t.type_ == str
        return [IsIns(v=v, type_=str)]

    def gen(self, to_name: str, type_: Type, context: Context, manager: TypeChecker) -> Iterable[OpCode]:
        warning('TODO: to be implemented')
        return [Gen(var=to_name, type_=type_, impl=None)]


class FunctionTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, FunctionType)

    # def typecheck(self, v: Any, t: 'Type', context: Context, manager: TypeChecker) -> bool:
    #     info(f'typecheck:')
    #     info(f'term = {getattr(v, "__name__", str(v))}, type = {t}')
    #     info(f'context = {context}')
    #     info(f'config = {manager.config}')
    #     assert t == str
    #     res = isinstance(v, str)
    #     info(f'typed? = {res}')
    #     return res

    def typecheck_codes(self, v: Any, t: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        info('-' * 10 + ' ' + self.__class__.__name__ + ' ' + '-' * 10)
        info(f'typecheck_codes:')
        info(f'  term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'  context = {context}')
        assert isinstance(t, FunctionType)

        args = t.args_type.args_type
        debug(f'arguments = {args}')
        for x0, t0 in args.items():
            debug(x0)
            debug(t0)

        # now debugging
        # name_type_pairs = [(manager.name(x), t) for x, t in args.items()]
        name_type_pairs = [(x, t) for x, t in args.items()]
        opcodes = list(flatten(
            [manager.gen(to_name=x, type_=t, context=context) for x, t in name_type_pairs]))
        var_list = [x for x, t in name_type_pairs]
        debug(opcodes)
        debug(var_list)

        to_name = manager.name('v')
        app = Apply(func=v, args=var_list, to=to_name)

        tc_codes = manager.typecheck(to_name, t.return_type, context=context)

        res = opcodes + [app] + tc_codes
        info(f'generated opcodes  = {pformat(res)}')
        return res

    def gen(self, to_name: str, type_: Type, context: Context, manager: TypeChecker) -> Iterable[OpCode]:
        warning('TODO: to be implemented')
        return [Gen(var=to_name, type_=type_, impl=None)]


class RefinementTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, RefinementType)

    def typecheck_codes(self, v: Any, t: Type, context: Context,
                        manager: 'TypeChecker') -> Iterable[OpCode]:
        info('-' * 10 + ' ' + self.__class__.__name__ + ' ' + '-' * 10)
        info(f'typecheck_codes:')
        info(f'  term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'  context = {context}')
        assert isinstance(t, RefinementType)

        debug(f'{t.base_var=}')
        debug(f'{t.base_type=}')
        debug(f'{t.predicate=}')

        # base type check and assertion of refinement
        # TODO: context to be fixed.
        base_tc_codes = manager.typecheck(v, t.base_type, context=context)
        res = base_tc_codes + [Assert_(bind=(t.base_var, v), pred=t.predicate)]
        info(f'generated opcodes  = {pformat(res)}')
        return res

    def gen(self, to_name: str, type_: Type, context: Context,
            manager: TypeChecker) -> Iterable[OpCode]:
        assert isinstance(type_, RefinementType)
        info('-' * 10 + ' ' + self.__class__.__name__ + ' ' + '-' * 10)
        info(f'gen:')
        info(f'  base var = {type_.base_var}')
        info(f'  type of value = {type_}')
        info(f'  type text = {type_.text}')
        info(f'  to_name = {to_name}')
        res = manager.gen(to_name=type_.base_var, type_=type_.base_type, context=context) + [
            Assume_(bind=(type_.base_var, type_.base_var),
                    pred=type_.predicate)
        ]
        if to_name != type_.base_var:
            res += [Move(from_=type_.base_var, to=to_name)]
        info(f'generated opcodes  = {pformat(res)}')
        return res


class ListIntTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, Generic) and t.type_ == list[int]

    @staticmethod
    def is_list_int(l) -> bool:
        return all(map(lambda e: isinstance(e, int), l))

    def typecheck_codes(self, v: Any, t: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        return [IsIns(v=v, type_=None, func=ListIntTypeChecker.is_list_int)]

    @staticmethod
    def gen_list():
        "generate a random int number."
        warn('TODO: list generation to be fully implemented', UserWarning)
        len = abs(int(normalvariate(0, 20)))
        generated = [int(normalvariate(0, 20)) for _ in range(len)]
        debug(f'rand_list: {generated=}')
        return generated

    def gen(self, to_name: str, type_: Type, context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        return [Gen(var=to_name, type_=type_, impl=ListIntTypeChecker.gen_list)]


class UnionTypeChecker(TypeCheckerImpl):
    def can_handle(self, t: Type) -> bool:
        return isinstance(t, Sum)

    def typecheck_codes(self, v: Any, t: 'Type', context: Context, manager: 'TypeChecker') -> Iterable[OpCode]:
        info(
            f'get_opcodes: term = {getattr(v, "__name__", str(v))}, type = {t}')
        info(f'context = {context}')
        assert get_origin(t) == Union
        return [IsIns(v=v, type_=str)]


def set_defaults(tc: TypeChecker) -> TypeChecker:
    """
    set default type checkers.
    """
    tc.register(IntTypeChecker())
    tc.register(FloatTypeChecker())
    tc.register(StrTypeChecker())
    tc.register(FunctionTypeChecker())
    tc.register(RefinementTypeChecker())
    tc.register(ListIntTypeChecker())
    tc.register(UnionTypeChecker())
    return tc


__all__ = ['IntTypeChecker', 'StrTypeChecker', 'set_defaults']
