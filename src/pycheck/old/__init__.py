"""
Pycheck: refinement-type based type checker using PBRT.
"""
from importlib.metadata import version
# from inspect import Signature, signature
from logging import getLogger
from operator import attrgetter
from typing import Any

from .config import Config, Context
# from .core import Refinement, Testable
from .spec import spec
from .toplevel import check
from .type import ArgsType, FunctionType, RefinementType
from .typecheck import TypeChecker, TypeCheckerImpl

debug, info = attrgetter('debug', 'info')(getLogger(__name__))
__version__ = version(__name__)

# 型の記述方法変更中に使っているフラグ。True なら新ロジックが走る。
# https://github.ibm.com/SHINSA/pycheck/issues/6
USE_NEY_TYPES: bool = True

__all__ = [
    '__version__', 'ArgsType', 'FunctionType',
    'Config', 'Context',  # from config
    'RefinementType', 'spec',  # from core
    'TypeChecker', 'TypeCheckerImpl',  # from typecheck
    'check',
    'spec',  # from spec
]
