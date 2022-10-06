"""
Code generator from reftype spec.

Code generator has two sub-routines.
'gen_typecheck_code()' is for checking of a term with a type ('beta' in our paper),
'gen_gen_code()' is for generating a value of the specified type ('alpha' in our paper).
"""
from logging import getLogger
from pprint import pformat
from textwrap import indent
from typing import Any, TypeAlias

from lark import Tree

from ..parsing import reconstruct
from .const import Code, CodeGenContext, CodeGenResult

logger = getLogger(__name__)


def code_func_header(func_name: str, params: list[str]):
    "utility to created a function header."
    return f"def {func_name}({','.join(params)}):"


def gen_header_elements(context: CodeGenContext, func_only=False) -> (
        tuple[str, str, CodeGenContext] | tuple[str, CodeGenContext]):
    "utility to created the default function header."
    entry_point = f"f{context.get_fsuf()}"
    if func_only:
        return entry_point, context
    param = f"x{context.get_vsuf()}"
    return entry_point, param, context


def code_func(header: str, body: str):
    "ulitity to create a function definition."
    return header + "\n" + indent(body, ' '*2)


def comment_tc(ast: Tree):
    "generate a comment line (typecheck)."
    return f"# type check '{reconstruct(ast)}'\n"


def comment_gen(ast: Tree):
    "generate a comment line (gen)."
    return f"# gen a value of '{reconstruct(ast)}'\n"


def wrap_func(name: str, vars: list[str], inner_code: Code) -> Code:
    """
    wrap a function as an inner one (used in prod type).
    """
    func_body = inner_code.text + f"return {inner_code.entry_point}"
    # nest_func_code = f"def {name}({', '.join(vars)}):\n" + \
    #     indent(func_body, "  ")
    nest_func_code = code_func_header(name, vars) + "\n" + \
        indent(func_body, "  ")
    return Code(nest_func_code)


def gen_typecheck_base(
    value: Any,
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False
) -> CodeGenResult:
    "generate a code for typechecking the term with base types."
    # raise NotImplementedError("generator for base types is not implemented")
    func_name, param, context = gen_header_elements(context)
    code = code_func(code_func_header(
        func_name, [param]), comment_tc(ast) + "return True")
    return (
        Code(code, entry_point=func_name).fix_code(),
        context
    )


def gen_typecheck_list(
    value: Any,
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False
) -> Code:
    "generate a code for typechecking the term with product types."
    type_ = ast.children[0]
    logger.debug("element type = %s", type_)

    logger.info("generating code for element type")
    (element_type_code, context) = gen_typecheck_code(...,
                                                      type_, context, is_delta=True)
    logger.debug(element_type_code.text)

    logger.info("generating main code with elment type checking code")
    entry_point, param, context = gen_header_elements(context)
    body = f"return all(map({element_type_code.entry_point},{param}))"
    logger.info(body)

    generated = code_func(code_func_header(entry_point, [
        param]), element_type_code.text + body)
    return (Code(generated, entry_point=entry_point).fix_code(), context)


def gen_typecheck_ref(
    value: Any,
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False
) -> Code:
    "generate a code for typechecking the term with refinement types."
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
    comment = comment_tc(ast)
    code_body = comment + main_type_code.text + \
        f"return {main_type_code.entry_point}({param}) and ({reconstruct(predicate)})"
    code = code_func(code_head, code_body)
    logger.debug("\n%s", code)

    return (Code(code, entry_point=entry_point).fix_code(), context)


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


def gen_typecheck_func(
        value: Any,
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False
) -> CodeGenResult:
    "generate a code for typechecking the term with function types."
    params = ast.children[0]
    return_type = ast.children[1]

    logger.debug("params and types:")
    for ch in params.children:
        logger.debug("  %s", (ch.children[0], ch.children[1]))
    logger.debug("return type = %s", return_type)
    if len(params.children) == 0:
        raise NotImplementedError(
            "currently 0-argument function (= thunk) is not supported")
    if len(params.children) > 1:
        raise NotImplementedError(
            "currently more than binary function is not supported")

    var = str(params.children[0].children[0].children[0])
    var_type = params.children[0].children[1]
    logger.debug("param = %s", var)
    logger.debug("param type =  %s", var_type)

    # code generation starts

    # header
    logger.info("generating header")
    entry_point, param, context = gen_header_elements(context)
    header = code_func_header(entry_point, [param])
    logger.debug(header)

    logger.debug("generating return type checking code")
    (return_type_code, context) = gen_typecheck_code(..., return_type, context)

    x_tmp2 = f"x{context.get_vsuf()}"

    logger.debug("generating main code")
    comment = comment_tc(ast)

    # value generation
    logger.debug("generating value generator")
    # gen_code, context = gen_gen(var_type, lambda z: True, context)
    gen_code, context = gen_gen(var_type, "lambda z: True", context)

    body = comment + return_type_code.text + gen_code.text + \
        f"{var}={gen_code.entry_point}() # gen arg\n{x_tmp2}={param}({var})\nreturn {return_type_code.entry_point}({x_tmp2})"
    logger.debug(body)

    code = Code(code_func(header, body), entry_point=entry_point).fix_code()
    logger.debug(code.text)

    return (code, context)


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
    logger.info("\n%s", ast.pretty())
    try:
        method = METHOD_MAPPING[ast.data]
        result: CodeGenResult = method(value, ast, context, is_delta=is_delta)
        return result
    except KeyError as err:
        raise ValueError(
            f"invalid token type found in reftype: {ast.data}") from err

#
# random generation code
#


def gen_gen(type_: Tree, pred_func: Any, context: CodeGenContext) -> str:
    """
    generate a value of the specified type.

    'alpha' in our paper)
    """
    logger.info("generating generator code for type '%s', predicate func '%s'",
                reconstruct(type_), pred_func)
    logger.info(context)
    logger.info("\n%s", type_.pretty())
    try:
        method = GEN_METHOD_MAPPING[type_.data]

        result: CodeGenResult = method(type_, pred_func, context)
        code, context = result
        logger.info("gen code genereated:")
        logger.info("\n%s", code.text)
        return result
    except KeyError as err:
        raise ValueError(
            f"invalid token type found in reftype: {type_.data}") from err


def gen_gen_base(type_: Tree, pred_func: Any, context: CodeGenContext) -> CodeGenResult:
    """
    generate a code to generate a value of base types.
    """
    func_name, context = gen_header_elements(context, func_only=True)
    header = code_func_header(func_name, [])
    comment = comment_gen(type_)
    var = f"x{context.get_vsuf()}"
    body = (f"{var} = rand_int()\n" +
            f"b = ({pred_func})({var})\n" +
            "if not b:\n" +
            f"  raise PyCheckAssumeError(f'generated value {{{var}}} did not satisfy the assumption')\n" +
            f"return {var}")
    return Code(code_func(header, comment+body), entry_point=func_name).fix_code(), context


def gen_gen_list(type_: Tree, pred_func: Any, context: CodeGenContext) -> str:
    """
    generate a code to generate a value of list types.
    """
    raise NotImplementedError(
        "gen generator for list types is not implemented")


def gen_gen_ref(type_: Tree, pred_func: Any, context: CodeGenContext) -> CodeGenResult:
    """
    generate a code to generate a value of refinement types.
    """
    var = str(type_.children[0].children[0].children[0].children[0])
    base_ = type_.children[0].children[1]
    predicate = type_.children[1]
    logger.debug("var = %s", var)
    logger.debug("base type = %s", base_)
    logger.debug("predicate = %s", predicate)

    return gen_gen(
        base_,
        f"lambda {var}: {reconstruct(predicate)} and ({pred_func})({var})",
        context
    )


def gen_exist(x: str, e: str):
    "computes expression that is implied by 'exist x. e'."
    logger.info("generating exist")
    logger.debug((x, e))
    logger.warning("currently exists is not implemented")
    return "True"


def gen_gen_prod(type_: Tree, pred_func: Any, context: CodeGenContext) -> str:
    """
    generate a code to generate a value of product types.
    """
    # populate type information
    subtypes = []
    for ch in type_.children:
        if ch.data == "innertypedparam":  # childlen other than the last one
            logger.debug("var = %s", ch.children[0])
            logger.debug("type = %s", ch.children[1])
            subtypes.append((str(ch.children[0].children[0]), ch.children[1]))
        else:
            # probably the last element
            subtypes.append((None, ch))

    logger.debug(pformat(subtypes))
    if len(subtypes) > 2:
        raise NotImplementedError(
            "currently n-tuple, where n > 2, is not supported")

    # header
    entry_point, context = gen_header_elements(context, func_only=True)
    header = code_func_header(entry_point, [])

    # typecheck the second component
    tau2_code, context = gen_typecheck_code(..., subtypes[1][1], context)

    var = f"x{context.get_vsuf()}"
    phi_2 = f"lambda {var}: ({pred_func})(({subtypes[0][0]}, {var}))"
    logger.debug(phi_2)
    var2 = f"x{context.get_vsuf()}"
    code_exist = gen_exist(
        var2, f"{tau2_code.entry_point}({var2}) and ({phi_2})({var2})")
    phi_1 = f"lambda {subtypes[0][0]}: {code_exist}"
    logger.debug(phi_1)

    comment = comment_gen(type_)
    gen_tau1, context = gen_gen(subtypes[0][1], phi_1, context)
    gen_tau2, context = gen_gen(subtypes[1][1], phi_2, context)
    body = (
        comment +
        gen_tau1.text +
        f"{subtypes[0][0]} = {gen_tau1.entry_point}()\n" +
        gen_tau2.text +
        f"{var} = {gen_tau2.entry_point}()\n" +
        f"return ({subtypes[0][0]}, {var})"
    )
    logger.debug(body)

    return Code(code_func(header, body), entry_point=entry_point).fix_code(), context


def gen_gen_func(type_: Tree, pred_func: Any, context: CodeGenContext) -> str:
    """
    generate a code to generate a value of function types.
    """
    raise NotImplementedError(
        "gen generator for function types is not implemented")


GEN_METHOD_MAPPING = {
    'base_type': gen_gen_base,
    'list_type': gen_gen_list,
    'ref_type': gen_gen_ref,
    'prod_type': gen_gen_prod,
    'func_type': gen_gen_func
}
