"""
Code generator implementation from reftype spec.

Code generator has two types of sub-routines.
'gen_typecheck_code()' is for checking of a term with a type ('beta' in our paper),
'gen_gen_code()' is for generating a value of the specified type ('alpha' in our paper).
"""
from logging import getLogger
from pprint import pformat
from textwrap import indent
from typing import Any

from lark import Tree
from sympy import (And, Dummy, GreaterThan, Lambda, LessThan, S,
                   StrictGreaterThan, StrictLessThan, simplify, srepr, symbols)

from ..parsing import reconstruct
from .code_builder import CodeBuilder
from .const import Code, CodeGenContext, CodeGenResult
from .sympy_lib import Exist, Len

logger = getLogger(__name__)
aa = symbols('aa')


def code_func_header(func_name: str, params: list[str]):
    "utility to created a function header."
    return f"def {func_name}({','.join(params)}):"


def gen_header_elements(context: CodeGenContext, var_name="x", func_only=False) -> (
        tuple[str, str, CodeGenContext] | tuple[str, CodeGenContext]):
    "utility to created the default function header."
    entry_point = f"f{context.get_fsuf()}"
    if func_only:
        return entry_point, context
    param = f"{var_name}{context.get_vsuf()}"
    return entry_point, param, context


def code_func(header: str, body: str):
    "ulitity to create a function definition."
    return header + "\n" + indent(body, ' '*2)


def comment_u(msg):
    "generate a universal comment."
    return f"# {msg}\n"


def comment_tc(ast: Tree):
    "generate a comment line (typecheck)."
    return f"# type check '{reconstruct(ast)}'\n"


def comment_gen(ast: Tree):
    "generate a comment line (gen)."
    return f"# generate a value of '{reconstruct(ast)}'\n"


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
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False,  # pylint: disable=unused-argument
    **kwargs  # to ignore 'value' param
) -> CodeGenResult:
    "generate a code for typechecking the term with base types."
    builder = CodeBuilder(context)
    return builder.comment_tc(type_=ast).func().body("return S.true").code()


def gen_typecheck_list(
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False,  # pylint: disable=unused-argument
    **kwargs  # to ignore 'value' param # pylint: disable=unused-argument
) -> Code:
    "generate a code for typechecking the term with product types."
    type_ = ast.children[0]
    logger.debug("element type = %s", type_)

    logger.info("generating code for element type")
    (element_type_code, context) = gen_typecheck_code(
        ast=type_, context=context, is_delta=True
    )
    logger.info("generated code:\n%s", element_type_code.text)

    logger.info("generating main code")
    # entry_point, param, context = gen_header_elements(context)
    # body = f"return all(map({element_type_code.entry_point},{param}))"
    # logger.info(body)

    # generated = code_func(code_func_header(entry_point, [
    #     param]), element_type_code.text + body)
    # return (Code(generated, entry_point=entry_point).fix_code(), context)

    builder = CodeBuilder(context)
    return (builder
            .comment_tc(type_=ast)
            .func()
            .body(element_type_code.text)
            .body(f"return all(map({element_type_code.entry_point},{builder.params_[0]}))")
            .code())


def gen_typecheck_ref(
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False,  # pylint: disable=unused-argument
    **kwargs  # to ignore 'value' param # pylint: disable=unused-argument
) -> Code:
    "generate a code for typechecking the term with refinement types."
    var = ast.children[0].children[0].children[0]
    type_ = ast.children[0].children[1]
    predicate = ast.children[1]
    logger.debug("var = %s", (str(var.children[0]), var))
    logger.debug("type = %s", type_)
    logger.debug("predicate = %s", predicate)

    logger.info("generating code for main type")
    (main_type_code, context) = gen_typecheck_code(
        ast=type_, context=context, is_delta=True)
    logger.info("code for main type:\n%s", main_type_code.text)

    logger.info("generating main code with predicate")
    param = str(var.children[0])
    # entry_point = f"f{context.get_fsuf()}"
    # code_head = code_func_header(entry_point, [param])
    # comment = comment_tc(ast)
    # code_body = comment + main_type_code.text + \
    #     f"return {main_type_code.entry_point}({param}) and ({reconstruct(predicate)})"
    # code = code_func(code_head, code_body)
    builder = CodeBuilder(context)
    return (builder.comment_tc(type_=ast).func(params=[param]).body(main_type_code.text).
            body(f"return {main_type_code.entry_point}({param}) and ({reconstruct(predicate)})").code())


def gen_typecheck_prod(
    ast: Tree,
    context: CodeGenContext,
    is_delta: bool = False  # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for typechecking the term with product types."
    logger.info(ast.children)

    # currently only binary tuples (= pairs) are supported.
    assert len(ast.children) == 2

    ch = ast.children
    logger.info("var = %s", str(ch[0].children[0].children[0]))
    logger.info("type = %s:\n%s", reconstruct(
        ch[0].children[1]), ch[0].children[1].pretty())
    logger.info("second = %s", ch[1].pretty())

    logger.info("generating code for the first type...")
    result0 = gen_typecheck_code(ch[0].children[1], context, is_delta=True)
    logger.info(result0[0])
    logger.info(result0[1])

    logger.info("generating code for the second type...")
    result1 = gen_typecheck_code(
        ch[1], context=result0[1], is_delta=True)
    logger.info(result1[0])
    logger.info(result1[1])

    # wrap result1 with the variable above
    logger.info("wrapping the function above...")
    result2 = (CodeBuilder(result1[1]).comment("wrapped by a bound variable")
               .func(params=str(ch[0].children[0].children[0]))
               .body(result1[0].text)
               .body(f"return {result1[0].entry_point}")
               .code())
    logger.info("\n%s", result2[0].text)
    logger.info(result2[1])

    builder = CodeBuilder(context)
    return (builder
            .comment_tc(type_=ast)
            .func()
            .body(result0[0].text)
            .body(result2[0].text)
            .body(f"return {result0[0].entry_point}({builder.params_[0]}[0]) and {result2[0].entry_point}({builder.params_[0]}[0])({builder.params_[0]}[1])")
            .code())


def gen_typecheck_prod_experimental(
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
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False
) -> CodeGenResult:
    "generate a code for typechecking the term with function types."
    if is_delta:
        # return identity func
        builder = CodeBuilder(context)
        return builder.comment_tc(type_=ast).func().body("return S.true").code()

    params = ast.children[0]

    if len(params.children) == 0:
        raise NotImplementedError(
            "currently 0-argument function (= thunk) is not supported")
    if len(params.children) > 1:
        raise NotImplementedError(
            "currently more than binary function is not supported")

    param = params.children[0]
    var = str(param.children[0].children[0])
    var_type = param.children[1]
    return_type = ast.children[1]

    logger.info(param)
    logger.info(var)
    logger.info("param type = %s:\n%s", reconstruct(
        var_type), var_type.pretty())
    logger.info("return type = %s:\n%s", reconstruct(
        return_type), return_type.pretty())

    logger.info("generating random generator...")
    code0, context0 = gen_gen(var_type, lambda z: S.true, context)

    builder = CodeBuilder(context0).comment_tc(ast).func().body(code0.text)
    builder.body(f"{var} = {code0.entry_point}()")

    code1, _ = gen_typecheck_code(return_type, context0, is_delta=False)
    builder.body(code1.text)

    v2 = builder.v()

    builder.body(f"{v2} = {builder.params_[0]}({var})")
    builder.body(f"return {code1.entry_point}({v2})")
    return builder.code()


def gen_typecheck_func_experimental(
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False
) -> CodeGenResult:
    "generate a code for typechecking the term with function types."
    if is_delta:
        # return identity func
        builder = CodeBuilder(context)
        return builder.comment_tc(type_=ast).func().body("return S.true").code()

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
    # gen_code, context = gen_gen(var_type, "lambda z: True", context)
    gen_code, context = gen_gen(var_type, lambda z: S.true, context)

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
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False,
        **kwargs  # to ignore 'value' param # pylint: disable=unused-argument
) -> CodeGenResult:
    """
    (Entrypoint) generate a code for typechecking the term with the type.

    It returns a function version of 'beta' in our paper, which receives
    the typechecking target and returns a bool.
    This also receives a context that is used to keep variable name candidates,
    and returns the updated one.
    Current implementation also returns a string for function name that has been generated.

    ast: AST parsed by Lark parser.
    context: context object for generationg codes (including variable and function names).
    Flag is_delta is used to which should be returned among 'beta' and 'delta'.
    """
    logger.info("generating type checking code for type '%s'...",
                reconstruct(ast))
    logger.info("context = %s", context)
    logger.info("\n%s", ast.pretty())
    try:
        # dispatched by label of the root of the parse tree
        method = METHOD_MAPPING[ast.data]
        result: CodeGenResult = method(
            ast=ast, context=context, is_delta=is_delta
        )
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
    logger.info("parse tree of the type =\n%s", type_.pretty())
    try:
        # tag at the root of parse tree
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
    def calc_constraint(bound, expr, symb) -> tuple[tuple[int, int], str]:
        """
        returns integer bound (inclusive). None means infinity.

        symb is a free variable in expr.
        """
        logger.info("%s: %s", expr, srepr(expr))
        a, b = bound

        # TODO bound update is not complete.
        if expr == S.true:  # it's correct; do not fix.
            return (bound, 'True')
        elif expr.func == StrictGreaterThan and expr.args[0] == symb:
            # case of 'x > C'
            return ((expr.args[1] + 1, b), 'True')
        elif expr.func == GreaterThan and expr.args[0] == symb:
            # case of 'x >= C'
            return ((expr.args[1], b), 'True')
        elif expr.func == StrictLessThan and expr.args[0] == symb:
            # case of 'x < C'
            return ((a, min(b, expr.args[1] - 1) if b is not None else expr.args[1] - 1), 'True')
        elif expr.func == StrictLessThan and expr.args[1] == symb:
            # case of 'C < x'
            return ((max(a, expr.args[1] + 1) if a is not None else expr.args[1] + 1, b), 'True')
        elif expr.func == LessThan and expr.args[0] == symb:
            # case of 'x <= C'
            return ((a, expr.args[1]), 'True')
        elif expr.func == And:
            (b0,  _) = calc_constraint(bound, expr.args[0], symb)
            (b1, _) = calc_constraint(b0, expr.args[1], symb)
            return (b1, 'True')
        else:
            logger.warning("unsupported func: %s", expr.func)
            return (bound, 'True')

    logger.debug("--- gen_base ---")

    func_name, context = gen_header_elements(context, func_only=True)
    header = code_func_header(func_name, [])
    comment = comment_gen(type_)

    var = f"x{context.get_vsuf()}"

    # trying new architecture

    helper = CodeBuilder(context)

    type_str = reconstruct(type_)
    logger.info("base type (in str) = %s", type_str)
    match type_str:
        case 'int':
            w = Dummy('w')
            logger.info("gen_int")
            logger.info(pred_func(w))
            logger.info(srepr(pred_func(w)))
            expr = simplify(pred_func(w))  # testing
            logger.info(expr)
        case _:
            raise ValueError(f"unsuported base type: {type_str}")

    _aa = helper.v()
    aa = symbols(_aa)
    logger.debug(aa)
    logger.debug(srepr(pred_func(aa)))
    expr = simplify(pred_func(aa))  # testing
    # expr = pred_func(aa)
    logger.debug("%s: %s", expr, srepr(expr))
    ((lower, upper), assume_phrase) = calc_constraint((None, None), expr, aa)
    logger.debug(((lower, upper), assume_phrase))
    # if expr == True:  # it's correct; do not fix.
    #     rand_int_phrase = "rand_int()"
    #     assume_phrase = "True"
    # elif expr.func == StrictGreaterThan and expr.args[0] == aa:
    #     rand_int_phrase = f"rand_int(min_={expr.args[1]+1})"
    #     assume_phrase = "True"
    # elif expr.func == GreaterThan and expr.args[0] == aa:
    #     rand_int_phrase = f"rand_int(min_={expr.args[1]})"
    #     assume_phrase = "True"
    # elif expr.func == And:
    #     logger.debug(expr.args[0])
    #     logger.debug(expr.args[1])
    # else:
    #     logger.warning(f"unsupported func: {expr.func}")
    min_phrase = f"min_={lower}, " if lower is not None else ""
    max_phrase = f"max_={upper}" if upper is not None else ""
    rand_int_phrase = f"rand_int({min_phrase}{max_phrase})"

    body = (f"{var} = {rand_int_phrase}\n" +
            f"b = {assume_phrase}\n" +
            "if not b:\n" +
            f"  raise PyCheckAssumeError(f'generated value {{{var}}} did not satisfy the assumption')\n" +
            f"return {var}")
    return Code(code_func(header, comment+body), entry_point=func_name).fix_code(), context


def gen_inner_gen(base: Tree, context: CodeGenContext) -> CodeGenResult:
    "generates inner gen function used in list generation."
    logger.debug("generating header")
    entry_point, param, context = gen_header_elements(context, var_name="ps")
    header = code_func_header(entry_point, [param])

    # code to gen 'car' of the list
    var1 = f"x{context.get_vsuf()}"
    gen_var1, context = gen_gen(base, lambda z: S.true, context)  # TODO
    # experimental: newer vesion
    gen_var1, context = gen_gen(base, lambda y: Exist(
        "z", "delta(list[base]) z and ps0(Cons(y, z))"), context)

    # code to gen 'cdr' of the list
    var2 = f"x{context.get_vsuf()}"

    body = ("if rand_bool():\n" +
            "  # generating []\n" +
            "  b = ps0([])\n" +
            "  if not b:\n" +
            "    raise PyCheckAssumeError(f'generated value [] did not satisfy the assumption')\n" +
            "  return []\n" +
            "# generating a::l\n" +
            # "return [1,2,3] # TODO\n" +
            gen_var1.text +
            f"{var1} = {gen_var1.entry_point}() # gen car # TODO\n" +
            f"{var2} = {entry_point}(lambda z: ps0([{var1}]+z)) # gen cdr\n" +
            f"return [{var1}] + {var2}"
            )
    code = Code(code_func(header, comment_u("inner_gen")+body),
                entry_point=entry_point).fix_code()
    return code, context


def gen_gen_list(type_: Tree, pred_func: Any, context: CodeGenContext) -> str:
    """
    generate a code to generate a value of list types.
    """
    base = type_.children[0]
    logger.debug("element type = %s", base)

    # logger.info("generating code for element type")
    # (element_type_code, context) = gen_typecheck_code(...,
    #                                                   type_, context, is_delta=True)
    # logger.debug(element_type_code.text)

    # logger.info("generating main code with elment type checking code")
    # entry_point, param, context = gen_header_elements(context)
    # body = f"return all(map({element_type_code.entry_point},{param}))"
    # logger.info(body)

    # header
    logger.debug("generating header")
    entry_point, context = gen_header_elements(context, func_only=True)
    header = code_func_header(entry_point, [])

    comment_ = comment_gen(type_)

    logger.debug("generating inner gen")
    inner_gen, context = gen_inner_gen(base, context)
    body = inner_gen.text + \
        f"return {inner_gen.entry_point}({srepr(pred_func)})"

    code = Code(code_func(header, comment_ + body),
                entry_point=entry_point).fix_code()
    logger.debug(code)

    return code, context


def gen_gen_ref(type_: Tree, pred_func: Any, context: CodeGenContext) -> CodeGenResult:
    """
    generate a code to generate a value of refinement types.
    """
    logger.debug("--- gen_ref ---")
    var = str(type_.children[0].children[0].children[0].children[0])
    base_ = type_.children[0].children[1]
    predicate = type_.children[1]
    logger.debug("var = %s", var)
    logger.debug("base type = %s", base_)
    logger.debug("predicate = %s", predicate)

    # implementing...
    # eval_refinement(reconstruct(predicate), var)

    # old
    # def new_pred_func(x):
    #     return S(reconstruct(predicate)
    #              ).subs(symbols(var), x) & pred_func(x)

    # new
    builder = CodeBuilder(context)

    x = symbols(builder.v())
    logger.info(pred_func(x))

    new_pred_func = Lambda(x, S(reconstruct(predicate)).subs(
        symbols(var), x) & pred_func(x))

    return gen_gen(
        base_,
        new_pred_func,
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
    tau2_code, context = gen_typecheck_code(
        ast=subtypes[1][1], context=context, is_delta=True)
    logger.info("code for tau_2\n%s", tau2_code.text)

    var = f"x{context.get_vsuf()}"

    phi_2 = f"lambda {var}: ({pred_func})(({subtypes[0][0]}, {var}))"
    logger.info("phi_2")
    logger.info(phi_2)
    logger.info(S(phi_2))

    var2 = f"x{context.get_vsuf()}"
    code_exist = f"Exist({var2}, ({tau2_code.entry_point}({var2})) & ({var}({var2})))"
    # code_exist = gen_exist(
    #     var2, f"{tau2_code.entry_point}({var2}) and ({phi_2})({var2})")
    phi_1 = f"lambda {subtypes[0][0]}: {code_exist}"
    logger.info("phi_1")
    logger.info(phi_1)
    logger.info(S(phi_1, locals={'Exist': Exist}))

    comment = comment_gen(type_)
    gen_tau1, context = gen_gen(subtypes[0][1], S(phi_1), context)
    gen_tau2, context = gen_gen(subtypes[1][1], S(phi_2), context)
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
    # populate type information
    argtypes = []
    for ch in type_.children[0].children:
        if ch.data == "typedparam":  # childlen other than the last one
            # logger.debug("var = %s", ch.children[0])
            # logger.debug("type = %s", ch.children[1])
            argtypes.append((str(ch.children[0].children[0]), ch.children[1]))
    # probably the last element
    rettype = type_.children[1]

    logger.debug(pformat(argtypes))
    logger.debug(rettype)

    if len(argtypes) != 1:
        raise NotImplementedError(
            f"currently only unary function is supported, but n={len(argtypes)} was given")

    # use new helper to generate code
    helper = CodeBuilder(context)

    # header
    helper.header(num_args=0)
    logger.debug(helper.header_)

    # comment
    helper.comment_gen(type_)
    logger.debug(helper.comment_)

    # generated func
    helper2 = CodeBuilder(context)
    var = argtypes[0][0]
    helper2.header(params=[var])
    helper2.comment("generated func def.")

    # type check the arg
    code3, context = gen_typecheck_code(..., argtypes[0][1], context)

    # gen return value
    code4, context = gen_gen(rettype, lambda z: "True", context)

    helper2.body(
        code3.text +
        code4.text +
        f"if rand_bool() or {code3.entry_point}({var}):\n" +
        f"  return {code4.entry_point}()\n" +
        f"else:\n" +
        f"  raise PyCheckFailError"
    )

    code2 = helper2.code()
    helper.body(code2.text +
                f"return {code2.entry_point}")

    code = helper.code()
    logger.debug("\n%s", code.text)

    return code, context
    raise NotImplementedError(
        "gen generator for function types is not implemented")


GEN_METHOD_MAPPING = {
    'base_type': gen_gen_base,
    'list_type': gen_gen_list,
    'ref_type': gen_gen_ref,
    'prod_type': gen_gen_prod,
    'func_type': gen_gen_func
}
