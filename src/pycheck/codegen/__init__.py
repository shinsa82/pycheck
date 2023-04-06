"""
Entry point of code generator from reftype spec.
"""
from logging import getLogger
from typing import Any

from ..reftype import RefType
from .codegen import gen_gen, gen_typecheck_code
from .const import Code, CodeGenContext

logger = getLogger(__name__)


def code_gen(value: Any, reftype: RefType, is_delta=False) -> Code:
    """
    generate a typechecking code from reftype.

    codes are valid Python programs,
    assuming that random generator rand_<T> is provided.
    """
    logger.info("generating type checking code...")
    logger.info(
        "  Note: generated code assumes simply-typedness of the target term.")
    (code, _) = gen_typecheck_code(
        value=value, ast=reftype.ast, context=CodeGenContext(), is_delta=is_delta)
    logger.info("code generated: \n%s", code.text)
    return code
