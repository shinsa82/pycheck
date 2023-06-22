"""
Entry point of code generator from reftype spec.
"""
from logging import getLogger
from typing import Any

from sympy import srepr

from ..reftype import RefType
# from .codegen import gen_gen, gen_typecheck_code
from .codegen_new import CodeGen
from .const import Code, CodeGenContext

logger = getLogger(__name__)


def code_gen(reftype: RefType, mode="typecheck", is_delta=False, constraint=None) -> Code:
    """
    generate a typechecking (or generation) code from the given reftype.

    if mode is "typecheck", typechecking code will be generated. (default)
    alternatively, if it's "gen", generation code will.

    Generated codes will be valid Python programs,
      assuming that definitions for random generator rand_<T> would be provided.
    """
    logger.info("generating type checking code...")
    logger.info(
        "  Note: generated code assumes simply-typedness of the target term.")
    generator = CodeGen()
    if mode == "typecheck":
        (code, _) = generator.gen(
            ast=reftype.ast, context=CodeGenContext(), is_delta=is_delta)
    else:  # assume mode == "gen"
        (code, _) = generator.gen_gen(
            ast=reftype.ast, context=CodeGenContext(), constraint=constraint)
    # logger.info("code generated: \n%s", code.text)
    logger.info("code generated: \n%s", code)
    logger.info("code generated (srepr): \n%s", srepr(code))
    return code
