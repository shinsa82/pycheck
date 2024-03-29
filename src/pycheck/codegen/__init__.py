"""
Entry point of code generator from reftype spec.
"""
from logging import getLogger
from typing import Any

from sympy import srepr

from ..reftype import RefType
from .codegen_new import setup
from .const import Code, CodeGenContext, true_func
from .qe import qe

logger = getLogger(__name__)

setup()


def code_gen(reftype: RefType, mode="typecheck", is_delta=False, constraint=None) -> Code:
    """
    generate a typechecking (or generation) code from the given reftype.

    if mode is "typecheck", typechecking code will be generated. (default)
    alternatively, if it's "gen", generation code will.

    Generated codes will be valid Python programs,
      assuming that definitions for random generator rand_<T> would be provided.
    """
    logger.info("generating type checking/generator code...")
    logger.info(
        "  Note: generated code assumes simply-typedness of the target term.")
    # generator = CodeGen()
    if mode == "typecheck":
        # (code, _) = generator.gen(
        #     ast=reftype.ast, context=CodeGenContext(), is_delta=is_delta)
        (code, _) = reftype.type_obj.gen(
            context=CodeGenContext(),
            is_delta=is_delta
        )
    else:
        assert mode == "gen"
        if constraint is None:
            constraint = true_func()
        (code, _) = reftype.type_obj.gen_gen(
            context=CodeGenContext(),
            constraint=constraint)

    logger.info("code generated: \n%s", code)
    logger.info("code generated (srepr): \n%s", srepr(code))
    return code
