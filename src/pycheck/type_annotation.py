"""
Decorator and methods related to type annotation.
"""
from logging import getLogger
from typing import Any, Callable, TypeVar

from .const import REFTYPE, TypeStr
from .reftype import RefType
from .util import func_name

F = TypeVar('F', bound=Callable[..., Any])
logger = getLogger(__name__)


def reftype(type_: TypeStr) -> Callable[[F], F]:
    """
    Decorator for specifying typespec of a function.

    metadata object (of TypeSpec) including specified typespec is stored at special attribute
    ('__pycheck_spec__') of the decorated function.

    Args:
        typespec (str): typespec string.

    Returns:
        Callable: Original function
    """
    def _(f: F) -> F:
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
        logger.info('set typespec "%s" to "%s"', type_, func_name(f))
        # debug("trying to obtain caller's frame...")
        # st = stack(context=3)[1]
        # debug(st)
        # caller_frame = st.frame
        # debug(pformat(st.frame.f_locals))
        # typespec_data = TypeSpec(
        #     text=typespec, eager=eager, check_args=check_args, check_ret=check_ret,
        #     globals=caller_frame.f_globals, locals=caller_frame.f_locals)
        # if eager:
        #     typespec_data.parse()
        setattr(f, REFTYPE, RefType(type_))
        return f

    return _


def has_reftype(func: Callable[..., Any]) -> bool:
    "Returns True if the function has reftype."
    return hasattr(func, REFTYPE)


def get_reftype(func: Callable) -> RefType:
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
    logger.info('getting typespec of %s', func_name(func))
    if has_reftype(func):
        return getattr(func, REFTYPE)
    else:
        raise AttributeError(f"reftype is not assigned to {func}")
