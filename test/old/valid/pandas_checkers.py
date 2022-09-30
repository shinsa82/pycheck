"""
Typecheckers related to Pandas.
"""
from random import normalvariate
from typing import Any

from numpy.random import default_rng
from pandas import DataFrame, Series, set_option
from pycheck.config import Context
from pycheck.opcode import Gen, IsIns, OpCodes
from pycheck.type import Base, Type
from pycheck.typecheck import TypeChecker, TypeCheckerImpl


class SeriesIntChecker(TypeCheckerImpl):
    """
    type checker for Series[int].
    """
    rng = default_rng()

    @staticmethod
    def gen_list():
        n = abs(int(normalvariate(0, 20)))
        arr = SeriesIntChecker.rng.integers(
            low=-100, high=100, size=n, endpoint=True)
        return Series(arr)

    def can_handle(self, t: Type) -> bool:
        return isinstance(t, Base) and t.type_ == Series

    def typecheck_codes(self, v: Any, t: Type, context: Context, manager: 'TypeChecker') -> OpCodes:
        return [IsIns(v=v, func=lambda s: isinstance(s, Series) and s.dtype == 'int64')]

    def gen(self, to_name: str, type_: Type, context: Context, manager: 'TypeChecker') -> OpCodes:
        return [Gen(var=to_name, type_=type_, impl=SeriesIntChecker.gen_list)]
