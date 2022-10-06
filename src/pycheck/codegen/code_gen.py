"""
Dispatcher of code generator from reftype spec.
"""
from logging import getLogger
from typing import Any

from lark import Tree

from ..reftype import RefType
from .const import Code, CodeGenContext
from .generators import gen_typecheck_code

logger = getLogger(__name__)


def code_gen(value: Any, reftype: RefType) -> Code:
    """
    generate a typechecking code from reftype.

    codes are valid Python programs,
    assuming that random generator rand_<T> is provided.
    """
    logger.info("generating typechecking code...")
    logger.info("config: assuming simply-typedness of the term")
    (code, _) = gen_typecheck_code(
        value, reftype.ast, CodeGenContext())
    logger.info("code generated: \n%s", code.text)
    return code

