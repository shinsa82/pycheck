"base class of codegen."
from logging import getLogger
from pprint import pformat
from typing import Callable

from lark import Tree
from sympy import Dummy, Lambda, S

from ..parsing import reconstruct
from ..types import PycheckType
from .const import Code, CodeGenContext, CodeGenResult, true_func

logger = getLogger(__name__)


class CodeGenBase:
    """
    base class of codegen.

    dispatcher method is implemented here.
    """
    typecheck_method_mapping: dict[str, Callable]
    gen_method_mapping: dict[str, Callable]

    def __init__(self, typecheck_method_mapping, gen_method_mapping):
        "constructor. set method_mapping here."
        self.typecheck_method_mapping = typecheck_method_mapping
        self.gen_method_mapping = gen_method_mapping

    def gen(
        self,
        ast: Tree,
        type_obj: PycheckType,
        context: CodeGenContext,
        is_delta: bool = False,
        **kwargs,  # to processing options # pylint: disable=unused-argument
    ):
        "codegen entrypoint for typechecking code."
        logger.info("- generating type checking code for type '%s'...",
                    reconstruct(ast))
        logger.info("context = %s", context)
        logger.info("is delta? = %s", is_delta)
        logger.info("\n%s", ast.pretty())
        try:
            # dispatched by label of the root of the parse tree
            method = self.typecheck_method_mapping[ast.data]
            result: CodeGenResult = method(
                ast=ast, context=context, is_delta=is_delta, **kwargs
            )
            logger.info("- generated code = %s", result[0])
            return result
        except KeyError as err:
            raise ValueError(
                f"invalid root type found in reftype: {ast.data}") from err

    def gen_gen(
        self,
        ast: Tree,
        context: CodeGenContext,
        constraint: Callable = None,
        **kwargs,  # to processing options # pylint: disable=unused-argument
    ):
        "codegen entrypoint for typechecking code."
        if constraint is None:
            constraint = true_func()
        logger.info("+ generating value generation code for type '%s'...",
                    reconstruct(ast))
        logger.info("context = %s", context)
        logger.info("constraint = %s", constraint)
        logger.info("\n%s", ast.pretty())
        try:
            # dispatched by label of the root of the parse tree
            method = self.gen_method_mapping[ast.data]
            result: CodeGenResult = method(
                ast=ast, context=context, constraint=constraint, **kwargs
            )
            logger.info("+ generated code = %s", result[0])
            return result
        except KeyError as err:
            raise ValueError(
                f"invalid root type found in reftype: {ast.data}") from err
