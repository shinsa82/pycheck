"""
Utilities for type normalization.
"""
from inspect import Parameter, Signature, signature
from typing import Any, Callable, Iterable

from pycheck.type import Base, FunctionType, Generic, RefinementType, Sum, Type
from pycheck.util import get_logger

debug, info, warning, _, _ = get_logger(__name__)


def project(kwargs: dict[str, Any], args: Iterable[str]) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if k in args}


def fusion_predicates(f: Callable, f_var: str, g: Callable, g_var: str) -> Callable:
    "fusion of two functions. used by normalization of nested refinement types."
    f_sig = signature(f)
    g_sig = signature(g)
    f_vars = f_sig.parameters.keys()
    g_vars = g_sig.parameters.keys()
    assert f_var in f_vars
    assert g_var in g_vars
    assert f_var not in g_vars
    assert f_var != g_var

    debug(f'params of f = {f_vars}')
    debug(f'params of g = {g_vars}')

    h_vars = (f_vars | g_vars) - {g_var}
    debug(f'params of fusion = {h_vars}')

    sig = Signature(parameters=[Parameter(
        v, kind=Parameter.POSITIONAL_OR_KEYWORD) for v in h_vars])

    def h(**kwargs):
        debug(f'args = {kwargs}')
        f_ba = f_sig.bind(**project(kwargs, f_vars))
        debug(f'f args = {f_ba.args}, {f_ba.kwargs}')
        kwargs[g_var] = kwargs[f_var]
        del kwargs[f_var]
        g_ba = g_sig.bind(**project(kwargs, g_vars))
        debug(f'g args = {g_ba.args}, {g_ba.kwargs}')
        return f(*f_ba.args, **f_ba.kwargs) and g(*g_ba.args, **g_ba.kwargs)
    h.__signature__ = sig
    return h


def complete(type_: Type) -> Type:
    """
    complete omitted base variable in a refinement types in an environment.

    Example:
    'l: { list[int] | lambda l: len(l)>0} -> int'
    can be completed to
    'l: {l: list[int] | lambda l: len(l)>0} -> int'
    """
    def _complete(var, t):
        "if t is a refinement type and has no base variable, complete it with 'var'."
        if isinstance(t, RefinementType):
            if t.base_var == '':
                # when var: t where t = "{ t2 | pred }"
                debug('base variable is empty!')
                t.base_var = var
                t.base_type = _complete(var, t.base_type)
                return t
            else:
                # when var: t where t = "{ x: t2 | pred }"
                t.base_type = _complete(t.base_var, t.base_type)
                return complete(t)
        else:
            return t

    if isinstance(type_, Base):
        return type_
    elif isinstance(type_, Generic):
        return type_
    elif isinstance(type_, Sum):
        return type_
    elif isinstance(type_, FunctionType):
        for v, t in type_.args:
            _complete(v, t)
        return type_
    elif isinstance(type_, RefinementType):
        return type_
    else:
        raise ValueError(f"unknown type: {type_}")


def normalize(type_: Type) -> Type:
    """
    normalize a type by flattening nested refinement types.
    """
    if isinstance(type_, Base):
        return type_
    elif isinstance(type_, Generic):
        return type_
    elif isinstance(type_, Sum):
        info(type_.choices)
        return Sum(
            type_name=type_.type_name,
            dirty=True,
            type_=None,
            choices=[normalize(t) for t in type_.choices]
        )
    elif isinstance(type_, FunctionType):
        # TODO: change to non-destructive construction...
        for v, t in type_.args.args_type.items():
            type_.args.args_type[v] = normalize(t)
        type_.return_type = normalize(type_.return_type)
        return type_
    elif isinstance(type_, RefinementType):
        info('-- reftype norm. --')
        base_type = normalize(type_.base_type)
        info(f"base var (outer) = {type_.base_var}")
        info(f"base type (outer) = {base_type}")
        info(f"predicate (outer) = {type_.predicate}")
        info(f"signature (outer) = {type_.signature}")
        if isinstance(base_type, RefinementType):
            # if nested refinement type
            info('base type is also refunement type:')
            info(f"base var (inner) = {base_type.base_var}")
            info(f"base type (inner) = {base_type.base_type}")
            info(f"predicate (inner) = {base_type.predicate}")
            info(f"signature (inner) = {base_type.signature}")
            info('do predicate fusion...')
            res = RefinementType(
                type_name=type_.type_name, type_=None, dirty=True,
                base_var=type_.base_var,
                base_type=base_type.base_type,
                predicate=fusion_predicates(type_.predicate, type_.base_var, base_type.predicate, base_type.base_var))
            info(f'after normalization = {res}')
            return res
        else:
            info('-- exit --')
            return type_
    else:
        raise ValueError(f"unknown type: {type_}")
