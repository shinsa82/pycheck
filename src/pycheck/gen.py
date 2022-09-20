"""Generators."""
from collections.abc import Callable
from functools import cache, partial
from inspect import Signature
from itertools import repeat, starmap
from logging import getLogger
from operator import attrgetter
from random import normalvariate
from typing import Annotated, Any, OrderedDict, get_args, get_origin

from pandas import Series as PandasSeries

import pycheck.typecheck as tc
from pycheck.type import RefinementType

from .core import Series, Type

debug, info, warning = attrgetter(
    'debug', 'info', 'warning')(getLogger(__name__))


def WIP_type(obj, t):
    raise NotImplementedError(f'{obj} for type {t} is WIP')


def generated_func(params_type, return_type, t=None, context=None):
    "generated function for a function type"
    def _(*args):
        info('evaluating generated function body')
        debug(f'#args = {len(args)}')
        assert len(args) == len(params_type)
        debug('checking argument types...')
        starmap(args, params_type)
        for arg_, type_ in zip(args, params_type):
            tc.typecheck(arg_, type_, context=context)
        debug('OK.')
        info('generating return value...')
        ret = gen(return_type)
        debug(f'generated return value = {ret}')
        # return cache(ret)
        return ret
    return _
    # return WIP_type('generated value', t)


def gen(t: Any, context=None) -> Any:
    info(f'generating a value of type {t}...')
    if context:
        info(f'context = {context}')

    # sanity check
    assert isinstance(t, Type), f'generation of type {t} is not supported'

    if t is int:
        generated = int(normalvariate(0, 20))
    elif isinstance(t, Signature):  # function signature
        generated = {}
        for param in t.parameters.values():
            debug(f'generating value for {param.name}')
            typ = param.annotation
            generatad_ = gen(typ, context=generated)
            generated[param.name] = generatad_
            if hasattr(generatad_, '__name__'):
                debug('setting function __name__ and __qualname__')
                generatad_.__name__ = f'gen_{param.name}'
                generatad_.__qualname__ = f'gen_{param.name}'
    elif isinstance(t, RefinementType):
        debug('refinement type (new)...')
        base = t.base
        pred = t.predicate
        debug(f'base type = {base}')
        debug(f'refinement var = {t.var}')
        debug(f'refinement = {pred}')
        while True:
            debug('generating base value...')
            base_generated = gen(base)
            debug('refinement check...')
            tmp_context = context | {t.var: base_generated}
            debug(f'context for refinement check: {tmp_context}')
            ref_check_res = pred(**tmp_context)
            debug(f'refinement predicate satisfiled? = {ref_check_res}')
            if ref_check_res:
                break
            info(f'refinement checking failed. retry generation')
        generated = base_generated
    elif get_origin(t) is Annotated:
        debug('refinement type...')
        (base, ref) = get_args(t)
        pred = ref.predicate
        debug(f'base type = {base}')
        debug(f'refinement = {ref}')
        while True:
            debug('generating base value...')
            base_generated = gen(base)
            debug('refinement check...')
            tmp_context = context | {ref.var: base_generated}
            debug(f'context for refinement check: {tmp_context}')
            ref_check_res = pred(**tmp_context)
            debug(f'refinement predicate satisfiled? = {ref_check_res}')
            if ref_check_res:
                break
            info(f'refinement checking failed. retry generation')
        generated = base_generated
    elif get_origin(t) is Callable:  # function type (appear as a parameter)
        params_type, return_type = get_args(t)
        debug(f'{params_type=}')
        debug(f'{return_type=}')
        generated = generated_func(params_type, return_type, t)
    elif get_origin(t) is list:  # list
        info('list type')
        t_base = get_origin(t)
        (t_item,) = get_args(t)
        debug(f'base type = {t_base}')
        debug(f'item type = {t_item}')
        debug('generating length...')
        l = gen(int)
        debug(f'length = {l}')
        debug('generating items...')
        pgen = partial(gen, context=context)
        generated = list(map(pgen, repeat(t_item, l)))
    elif get_origin(t) is Series:
        info('pandas.Series type')
        t_base = get_origin(t)
        (t_item,) = get_args(t)
        debug(f'base type = {t_base}')
        debug(f'item type = {t_item}')

        # generates pure list
        debug('generating list...')
        gen_list = gen(list[t_item], context=context)
        debug(f'generated list = {gen_list}')

        debug('converting to Series...')
        # TODO: use valid dtype instead
        generated = PandasSeries(gen_list, dtype=t_item)

    else:
        raise NotImplementedError(
            f'generator for type {t} has not been implemented yet')

    info(f'generated value = {generated}')
    return generated
