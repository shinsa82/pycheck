"""
Code generator from reftype spec.

Code generator has two sub-routines.
'gen_typecheck_code()' is for checking of a term with a type ('beta' in our paper),
'gen_gen_code()' is for generating a value of the specified type ('alpha' in our paper).
"""
from logging import getLogger
from textwrap import indent
from typing import Any, TypeAlias

from autopep8 import fix_code
from lark import Tree

from ..parsing import reconstruct
from .const import Code, CodeGenContext, CodeGenResult

logger = getLogger(__name__)


def gen_typecheck_base(
    value: Any,
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False
) -> CodeGenResult:
    "generate a code for typechecking the term with base types."
    # raise NotImplementedError("generator for base types is not implemented")
    f_name = f"f{context.get_fsuf()}"  # like f0, f1, ...
    code_func = f"""
    def {f_name}(x{context.get_vsuf()}):
        return True
    """
    return (
        Code(code_func, entry_point=f_name).fix_code(),
        context
    )


def gen_typecheck_list(value: Any, ast: Tree, context: CodeGenContext, as_func: bool = False) -> Code:
    raise NotImplementedError("generator for list types is not implemented")


def code_func_header(func_name: str, params: list[str]):
    return f"def {func_name}({','.join(params)}):"


def code_func(header: str, body: str):
    return header + "\n" + indent(body, ' '*2)


def gen_typecheck_ref(
    value: Any,
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False
) -> Code:
    "generate a code for typechecking the term with refinement types."
    logger.debug(ast.pretty())
    var = ast.children[0].children[0].children[0]
    type_ = ast.children[0].children[1]
    predicate = ast.children[1]
    logger.debug("var = %s", (str(var.children[0]), var))
    logger.debug("type = %s", type_)
    logger.debug("predicate = %s", predicate)

    logger.info("generating code for main type")
    (main_type_code, context) = gen_typecheck_code(..., type_, context, is_delta=True)
    logger.debug(main_type_code.text)

    logger.info("generating main code with predicate")
    param = str(var.children[0])
    entry_point = f"f{context.get_fsuf()}"
    code_head = code_func_header(entry_point, [param])
    code_body = main_type_code.text + \
        f"return {main_type_code.entry_point}({param}) and ({reconstruct(predicate)})"
    code = code_func(code_head, code_body)
    logger.debug("\n%s", code)

    return (Code(code, entry_point=entry_point).fix_code(), context)


def wrap_func(name: str, vars: list[str], inner_code: Code) -> Code:
    """
    wrap a function as an inner one.
    """
    func_body = inner_code.text + f"return {inner_code.entry_point}"
    nest_func_code = f"def {name}({', '.join(vars)}):\n" + \
        indent(func_body, "  ")
    return Code(nest_func_code)


def gen_typecheck_prod(
    value: Any,
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False
) -> CodeGenResult:
    "generate a code for typechecking the term with product types."
    # memo:
    # from the 2nd to the last type component,
    # need to wrap the generated func with variables appeared before that component.
    logger.debug(ast.pretty())
    assert len(ast.children) > 1
    variables = []  # list of variables
    wrapped_funcs = []  # outer faction names (p1, p2, ... in our paper)
    result_code = Code()

    for ch in ast.children:
        logger.debug(ch.pretty())
        if ch.data == "innertypedparam":  # childlen other than the last one
            logger.debug("var = %s", ch.children[0])
            logger.debug("type = %s", ch.children[1])

            (code, context) = gen_typecheck_code(
                None, ch.children[1], context)
            logger.debug(code.text)
            logger.debug(variables)
            logger.debug(context)

            if len(variables) > 0:  # excepr for the first
                logger.debug("wrapping the code with preceding variables...")
                func_name = f"f{context.get_fsuf()}"
                nest_func_code = wrap_func(
                    func_name, variables, code)
                logger.debug("\n%s", nest_func_code.text)
                result_code = result_code.append(nest_func_code)
                wrapped_funcs.append(func_name)
            else:
                result_code = result_code.append(code)
                wrapped_funcs.append(code.entry_point)

            result_code.fix_code()
            variables.append(str(ch.children[0].children[0]))
        else:
            assert len(variables) > 0
            logger.info("type = %s", ch)
            (code, context) = gen_typecheck_code(
                None, ch, context)
            logger.debug(code.text)
            logger.debug(variables)
            logger.debug(context)
            logger.debug("wrapping the code with preceding variables...")
            func_name = f"f{context.get_fsuf()}"
            nest_func_code = wrap_func(
                func_name, variables, code)
            logger.debug("\n%s", nest_func_code.text)
            result_code = result_code.append(nest_func_code)
            result_code.fix_code()
            wrapped_funcs.append(func_name)

    logger.debug("sub-functions:")
    logger.debug(result_code.text)
    logger.debug(variables)
    logger.debug(wrapped_funcs)

    # generates the final code
    entry_point = f"f{context.get_fsuf()}"
    arg = f"x{context.get_vsuf()}"

    num_args = len(wrapped_funcs)
    sub_args = [f"{arg}[{i}]" for i in range(num_args)]
    logger.debug(sub_args)

    calls = [call_code(*x) for x in [(wrapped_funcs[i],
                                      sub_args[:i], sub_args[i]) for i in range(num_args)]]
    final_code_body = 'return ' + ' and '.join(calls)
    logger.debug(final_code_body)

    final_code = f"def {entry_point}({arg}):" + "\n" + \
        indent(result_code.text + final_code_body, ' '*2)

    logger.debug("\n%s", Code(final_code).fix_code().text)

    result_code = Code(final_code).fix_code()
    result_code.entry_point = entry_point
    logger.debug(result_code.text)

    return (result_code, context)


def call_code(f, args1, arg2):
    "generate snippet to call sub-func. in prod types."
    call1 = f"{f}" if len(args1) == 0 else f"{f}({','.join(args1)})"
    call = f"{call1}({arg2})"
    logger.debug(call)
    return call


def gen_typecheck_func(value: Any, ast: Tree, context: CodeGenContext, as_func: bool = False) -> Code:
    raise NotImplementedError(
        "generator for function types is not implemented")


# mapping from type to generator function
METHOD_MAPPING = {
    'base_type': gen_typecheck_base,
    'list_type': gen_typecheck_list,
    'ref_type': gen_typecheck_ref,
    'prod_type': gen_typecheck_prod,
    'func_type': gen_typecheck_func
}


def gen_typecheck_code(
        value: Any,
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False
) -> CodeGenResult:
    """
    generate a code for typechecking the term with the type.

    It returns a function version of 'beta' in our paper, which receives
    the typechecking target and returns a bool.
    This also receives a context that is used to keep variable name candidates,
    and returns updated one.
    Current implementation also returns a string for function name that has been generated.

    Flag is_delta is used to which should be returned among 'beta' and 'delta'.
    """
    logger.info("generating code for type '%s'",
                reconstruct(ast))
    logger.info(context)
    try:
        method = METHOD_MAPPING[ast.data]
        result: CodeGenResult = method(value, ast, context, is_delta=is_delta)
        return result
    except KeyError as e:
        raise ValueError(
            f"invalid token type found in reftype: {ast.data}") from e
