"""
spec - Type specification (typespec) decorator
"""
from collections import OrderedDict
from dataclasses import dataclass
from inspect import signature, stack
from logging import getLogger
from operator import attrgetter
from pprint import pformat
from typing import Any, Callable, Mapping, TypeVar, Union

from .parser import parse
from .type import FunctionType, SignatureFunctionType, Type
from .type.normalization import normalize
from .util import func_name, get_logger

debug, info, warning, _, _ = get_logger(__name__)

PYCHECK_PROP_PREFIX = "pycheck"
PROP_SPEC = f"__{PYCHECK_PROP_PREFIX}_spec__"
# PROP_CHECK_ARGS = f"__{PYCHECK_PROP_PREFIX}_check_args__"
# PROP_CHECK_RET = f"__{PYCHECK_PROP_PREFIX}_check_ret__"

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class TypeSpec:
    """
    datatype for storing typespec.

    text: oroginal typespec text (= type assertion)
    ast: parsed AST object (subclass of type.Type) of the typespec
    globals: globals() of the caller of _spec
    locals: locals() of the caller of _spec
    """
    text: str = None
    ast: Type = None
    eager: bool = False
    check_args: bool = False
    check_ret: bool = False
    globals: Mapping = None
    locals: Mapping = None

    def parse(self):
        """
        parse typespec string using global and local envs in this object.
        """
        info(f'parsing typespec {self.text}...')
        debug('globals = ')
        debug(pformat(self.globals))
        debug('locals = ')
        debug(pformat(self.locals))

        self.ast = parse(
            self.text,
            globals_=self.globals | self.locals)
        info(f'parsed typespec (after normalization) = {pformat(self.ast)}')


def spec(typespec: str, eager=False, check_args=False, check_ret=False) -> Callable[[F], F]:
    """Decorator for specifying typespec of a function.

    metadata object (of TypeSpec) including specified typespec is stored at special attribute
    ('__pycheck_spec__') of the decorated function.

    Args:
        typespec (str): typespec string.
        eager (bool, optional): By defalt, typespec string will parsed when it'll be used.
            When set to True, it is parsed when evaluating the decorator.
            Defaults to False.
        check_args (bool, optional): **Not implemented:** Typechecks arguments at runtime.
            Defaults to False.
        check_ret (bool, optional): **Not implemented:** Typechecks return value at runtime.
        Defaults to False.

    Returns:
        callable: Original function
    """
    def _spec(f: F) -> F:
        """
        decorator function. see docstring of 'spec' for detail.

        typespec string will be evaluated using caller's global scope, 
        so all symbols in the string need to be resolved in that scope.
        """
        # setting hook properties
        # debug('current stack frames:')
        # for i, fi in enumerate(stack(context=3)):
        #     debug(f'** {i} **')
        #     debug(fi)
        info(f'set typespec "{typespec}" to {func_name(f)}')
        debug("trying to obtain caller's frame...")
        st = stack(context=3)[1]
        debug(st)
        caller_frame = st.frame
        debug(pformat(st.frame.f_locals))
        typespec_data = TypeSpec(
            text=typespec, eager=eager, check_args=check_args, check_ret=check_ret,
            globals=caller_frame.f_globals, locals=caller_frame.f_locals)
        if eager:
            typespec_data.parse()
        setattr(f, PROP_SPEC, typespec_data)
        return f

    return _spec


def has_typespec(func: Callable[..., Any]) -> bool:
    return hasattr(func, PROP_SPEC)


def typespec(func: Callable, raw=False) -> Union[FunctionType, TypeSpec]:
    """returns typespec assigned with the given function.

    Args:
        func (Callable): [description]
        raw (bool, optional): if True, TypeSpec object is returned. otherwise, typespec AST
            in TypeSpec will be returned. Defaults to False.

    Raises:
        NotImplementedError: [description]

    Returns:
        Union[FunctionType, TypeSpec]: TypeSpec object or raw AST in the object.
    """
    info(f'getting typespec of {func}')
    if has_typespec(func):
        info("obtaining type from spec decorator")
        if getattr(func, PROP_SPEC).ast is None:
            # if not AST is not used before, parse text to generate it.
            getattr(func, PROP_SPEC).parse()

        if raw:
            return getattr(func, PROP_SPEC)
        else:
            return getattr(func, PROP_SPEC).ast
    else:
        warning(
            "spec decoration not found. As a fallback, obtaining type from signature")
        raise NotImplementedError(
            'getting typespec from func sigunature is not implemented in this version')
        return SignatureFunctionType(signature(func))


__all__ = ["spec", "has_typespec", "typespec"]
