"new version of codegen."
from logging import getLogger
from pprint import pformat
from typing import Callable

from lark import Tree
from sympy import (ITE, And, Dummy, Function, GreaterThan, Integer, Lambda,
                   LessThan, Rational, S, StrictGreaterThan, StrictLessThan,
                   Symbol, ceiling, floor, simplify, srepr)
from sympy.utilities.misc import as_int

from ..const import PyCheckAssumeError, PyCheckFailError
from ..parsing import reconstruct
from ..random.random_generators import rand_bool, rand_int
from ..types import BaseType, FunctionType, ListType, ProdType, RefinementType
from .codegen_base import CodeGenBase
from .const import CodeGenContext, CodeGenResult, true_func
from .sympy_lib import (All, Cons, Exist, IsSorted, Len, List, ListSymbol, Map,
                        TupleSymbol)

logger = getLogger(__name__)


def tc_base(
    self: BaseType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to process options # pylint: disable=unused-argument
):
    "generate a code for typechecking the term with base types."
    return Lambda((Dummy('x'),), S.true), context


def tc_ref(
    self: RefinementType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to process options # pylint: disable=unused-argument
):
    "generate a code for typechecking the term with refinement types."
    logger.debug("var = %s", self.base_var)
    logger.debug("type = %s", self.base_type)
    logger.info("predicate = %s", self.predicate)

    logger.info("generating code for main type")
    (main_type_code, context) = self.base_type.gen(
        context=context, is_delta=True)
    logger.info("code for main type:\n%s", main_type_code)

    logger.info("generating main code with predicate")
    _x = Symbol(self.base_var)
    body = main_type_code(_x) & self.predicate
    logger.info('main code function body = %s', body)

    # Simplifying here causes an error when Len(l) is used.
    # So moved simplify later, into gen method.
    # lam_body = simplify(body)
    return Lambda(_x, body), context


def tc_list(
    self: ListType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to process options # pylint: disable=unused-argument
):
    "generate a code for typechecking the term with list types."
    logger.debug("element type = %s", self.base_type)

    logger.info("generating code for element type")
    (element_type_code, context) = self.base_type.gen(
        context=context, is_delta=True
    )
    logger.info("generated code:\n%s", element_type_code)

    logger.info("generating main code")
    _x = ListSymbol(f'x{context.get_vsuf()}')
    return Lambda((_x,), All(Map(element_type_code, _x))), context


def tc_prod(
    self: ProdType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to ignore 'value' param # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for typechecking the term with product types."
    logger.info("var = %s", self.first_var)
    logger.info("type = %s", self.first_type)
    logger.info("second = %s", self.second_type)

    first_type_code, context = self.first_type.gen(context, is_delta=True)
    logger.info(first_type_code)
    second_type_code, context = self.second_type.gen(context, is_delta=True)
    _y = Symbol(self.first_var)
    _x = TupleSymbol(f'x{context.get_vsuf()}')
    second_type_code = Lambda(_y, second_type_code)
    logger.info(second_type_code)
    ret = Lambda((_x,), first_type_code(
        _x[0]) & second_type_code(_x[0])(_x[1]))
    logger.info(ret)
    return ret, context


def tc_func(
    self: FunctionType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    """
    generate a code for typechecking the term with function types.

    gen() for other types return SymPy expression.
    While this class's gen() returns normal Python function.
    """
    if is_delta:
        # return identity func
        return Lambda(Dummy('x'), S.true), context

    # param = params.children[0]
    # var = str(param.children[0].children[0])
    x_ = Symbol(self.param_var)

    logger.info(self.param_var)
    logger.info("param type = %s", self.param_type)
    logger.info("return type = %s", self.return_type)

    # _f = Function(var)

    gen_code, context = self.param_type.gen_gen(
        context=context, constraint=Lambda((Dummy('x'),), S.true))

    tc_code, context = self.return_type.gen(context=context, is_delta=False)

    def ret(f):
        v = gen_code()
        logger.info("v = %s", v)
        r = f(v)
        logger.info("r = %s", r)
        return tc_code(r).subs(x_, v)

    # ret = Lambda((_f,), tc_code(_f(gen_code())))
    logger.info(ret)
    return ret, context


def calc_constraint(expr, bound, symb) -> tuple[tuple[int, int], str]:
    """
    returns integer bound (inclusive). None means infinity.

    expr is a constraint expression.
    bound is current interger interval.
    symb is a free variable in expr.
    """
    # logger.info("%s: %s", expr, srepr(expr))
    low, upp = bound

    # TODO bound update is not complete.
    if expr == S.true:  # it's correct; do not fix.
        return (bound, Lambda((symb,), S.true))
    elif expr.func == StrictGreaterThan and expr.args[0] == symb:
        # case of 'x > C'
        c_ = expr.args[1]
        if isinstance(c_, Integer):
            c_ = as_int(c_ + 1)
        else:  # Rational
            c_ = as_int(ceiling(c_))
        low = c_ if low is None else max(low, c_)
        return ((low, upp), Lambda((symb,), S.true))
    elif expr.func == GreaterThan and expr.args[0] == symb:
        # case of 'x >= C'
        c_ = expr.args[1]
        if isinstance(c_, Integer):
            c_ = as_int(c_)
        else:  # Rational
            c_ = as_int(ceiling(c_))
        low = c_ if low is None else max(low, c_)
        return ((low, upp), Lambda((symb,), S.true))
    elif expr.func == StrictLessThan and expr.args[0] == symb:
        # case of 'x < C'
        c_ = expr.args[1]
        if isinstance(c_, Integer):
            c_ = as_int(c_ - 1)
        else:  # Rational
            c_ = as_int(floor(c_))
        upp = c_ if upp is None else min(upp, c_)
        return ((low, upp), Lambda((symb,), S.true))
    elif expr.func == LessThan and expr.args[0] == symb:
        # case of 'x <= C'
        c_ = expr.args[1]
        if isinstance(c_, Integer):
            c_ = as_int(c_)
        else:  # Rational
            c_ = as_int(floor(c_))
        upp = c_ if upp is None else min(upp, c_)
        return ((low, upp), Lambda((symb,), S.true))
    elif expr.func == And:
        (b0, ass1) = calc_constraint(expr.args[0], bound, symb)
        (b1, ass2) = calc_constraint(expr.args[1], b0, symb)
        return (b1, Lambda((symb,), (ass1(symb)) & (ass2(symb))))
    else:
        logger.warning("unsupported func: %s", expr.func)
        return (bound, Lambda((symb,), expr))


def gen_base(
    self: BaseType,
    context: CodeGenContext,
    constraint: Callable,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for generating a value of base types."
    match self.type:
        case 'int':
            def f(env=None):
                _const = constraint

                def _():
                    if env:
                        constraint = _const.subs(env)
                    else:
                        constraint = _const

                    _w = Dummy('w')
                    _c = simplify(constraint(_w))
                    logger.info("original constraint: %s", constraint)
                    logger.info("simplified constraint: %s", _c)
                    logger.info(srepr(_c))
                    bound, assumption = calc_constraint(_c, (None, None), _w)
                    logger.info((bound, assumption))
                    l, u = bound

                    v = rand_int(min_=l, max_=u)
                    # if not constraint(v):
                    if not assumption(v):
                        raise PyCheckAssumeError(
                            f'generated value {v} did not satisfy the assumption {constraint}')
                    return v
                return _
            return f, context
        case 'bool':
            def f(env=None):
                return lambda: rand_bool()
            return f, context
        case _:
            raise ValueError(f"unsupported base type: {self.type}")


def gen_ref(
    self: RefinementType,
    context: CodeGenContext,
    constraint: Callable,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for generating a value of refinement types."
    logger.info("var = %s", self.base_var)
    logger.info("base type = %s", self.base_type)
    logger.info("predicate = %s", self.predicate)

    # implementing...
    # eval_refinement(reconstruct(predicate), var)

    # old
    # def new_pred_func(x):
    #     return S(reconstruct(predicate)
    #              ).subs(symbols(var), x) & pred_func(x)

    if isinstance(self.base_type, ProdType):
        _x = TupleSymbol(self.base_var)
    else:
        _x = Symbol(self.base_var)
    new_constraint = Lambda((_x,),
                            self.predicate & (constraint(_x)))
    logger.info(new_constraint)

    code, context = self.base_type.gen_gen(
        context=context, constraint=new_constraint)

    logger.info(code)

    def f(env=None):
        return code(env)
    return f, context


def gen_prod(
    self: ProdType,
    context: CodeGenContext,
    constraint: Callable,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for generating a value of product types."
    subtypes = []
    # for ch in ast.children:
    #     if ch.data == "innertypedparam":  # childlen other than the last one
    #         logger.info("var = %s", ch.children[0])
    #         logger.info("type = %s", ch.children[1])
    #         subtypes.append(
    #             (str(ch.children[0].children[0]), ch.children[1]))
    #     else:
    #         # probably the last element
    #         subtypes.append((None, ch))

    # logger.info("subtypes:")
    # for subtype in subtypes:
    #     logger.info(f"%s: %s", subtype[0], reconstruct(subtype[1]))
    # # logger.info(pformat(subtypes))
    # if len(subtypes) > 2:
    #     raise NotImplementedError(
    #         "currently n-tuple (where n > 2) is not supported")

    logger.info("first var = %s", self.first_var)
    logger.info("first type = %s", self.first_type)
    logger.info("second type = %s", self.second_type)

    # subtypes = [(self.first_var, self.first_type), (None, self.second_type)]
    x1 = Symbol(self.first_var)
    _x2 = Dummy('x2')
    _x3 = Dummy('x3')

    # codegen sigma(tau2)
    x2_tc_code, context = self.second_type.gen(
        context=context, is_delta=True)
    logger.info(x2_tc_code)

    const2 = Lambda((_x2,), constraint((x1, _x2)))  # here x1 is free
    logger.info("const2 = %s", const2)
    const1 = Lambda((x1,), Exist(_x3, x2_tc_code(_x3) & const2(_x3)))
    logger.info("const1 = %s", const1)

    code1, context = self.first_type.gen_gen(
        context=context, constraint=const1)
    # code2, context = self.second_type.gen_gen(
    #     context=context, constraint=const2(v1))

    def f(env=None):
        if env is None:
            env = {}

        def _():
            v1 = code1(env)()
            code2, context = self.second_type.gen_gen(
                context=CodeGenContext(),
                constraint=const2.subs({x1: v1}),
            )
            v2 = code2({x1: v1} | env)()
            return (v1, v2)
        return _
    return f, context


def gen_func(
    self: FunctionType,
    context: CodeGenContext,
    constraint: Callable,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for generating a value of product types."
    var = self.param_var
    x_ = Symbol(var)
    var_type = self.param_type
    return_type = self.return_type

    logger.info('---')
    # logger.info(param)
    logger.info("param name = %s", var)
    logger.info("param type = %s:\n%s", reconstruct(
        var_type), var_type.pretty())
    logger.info("return type = %s:\n%s", reconstruct(
        return_type), return_type.pretty())

    var_tc, context = self.gen(var_type, context=context)
    ret_gen, context = self.gen_gen(return_type, context=context)

    def f():
        return lambda x: ret_gen() if rand_bool() or var_tc(x) else PyCheckFailError

    return f, context


USE_EXIST = True


def gen_list(
    self: ListType,
    context: CodeGenContext,
    constraint: Callable,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for generating a value of product types."
    type_ = self.base_type
    logger.info("element type = %s", type_)

    # logger.info("generating code for element type")
    # (element_type_code, context) = self.gen(
    #     ast=type_, context=context, is_delta=True
    # )
    # logger.info("generated code:\n%s", element_type_code)

    def gen(constr, idx):
        logger.info("gen constraint: %s", constr)

        def f(env=None):
            if env is None:
                env = {}

            def _():
                context = CodeGenContext()
                if rand_bool(p=0.25):
                    logger.info("** nil branch")
                    if constr(List()) != S.true:
                        raise PyCheckAssumeError(
                            f'generated value {[]} did not satisfy the assumption {constr}')
                    return []
                else:
                    logger.info("** cons branch")
                    y_ = ListSymbol(f'y{idx}')
                    z_ = ListSymbol(f'z{idx}')
                    z_tc_code, context = self.base_type.gen(
                        context=context, is_delta=True)
                    logger.info(f"base type TC code = {z_tc_code}")
                    if USE_EXIST:
                        _constraint = Lambda((y_,), Exist(
                            z_, z_tc_code(z_) & constraint(Cons(y_, z_)).subs(env)))
                    else:
                        _constraint = Lambda((y_,), S.true)
                    y_gen, context = self.base_type.gen_gen(
                        constraint=_constraint, context=context)  # TODO
                    y = y_gen(env)()
                    z = gen(Lambda((z_,), constr(Cons(y, z_))),
                            idx+1)(env)()
                    return [y] + z
            return _
        return f
    return gen(constraint, 0), context


def setup():
    "add generator methods to PyCheckType. For the latest impl."

    BaseType.gen = tc_base
    BaseType.gen_gen = gen_base
    RefinementType.gen = tc_ref
    RefinementType.gen_gen = gen_ref
    ListType.gen = tc_list
    ListType.gen_gen = gen_list
    ProdType.gen = tc_prod
    ProdType.gen_gen = gen_prod
    FunctionType.gen = tc_func
    FunctionType.gen_gen = gen_func


class CodeGen(CodeGenBase):
    "new code generator that avoid to use symbolic boolean in SymPy."

    def __init__(self, **kwargs):
        "constructor. set method_mapping here."
        super().__init__(
            typecheck_method_mapping={
                'base_type': self.tc_base,
                'list_type': self.tc_list,
                'ref_type': self.tc_ref,
                'prod_type': self.tc_prod,
                'func_type': self.tc_func,
            },
            gen_method_mapping={
                'base_type': self.gen_base,
                'list_type': self.gen_list,
                'ref_type': self.gen_ref,
                'prod_type': self.gen_prod,
                'func_type': self.gen_func,
            }
        )

    def calc_constraint(self, expr, bound, symb) -> tuple[tuple[int, int], str]:
        """
        returns integer bound (inclusive). None means infinity.

        expr is a constraint expression.
        bound is current interger interval.
        symb is a free variable in expr.
        """
        # logger.info("%s: %s", expr, srepr(expr))
        low, upp = bound

        # TODO bound update is not complete.
        if expr == S.true:  # it's correct; do not fix.
            return (bound, S.true)
        elif expr.func == StrictGreaterThan and expr.args[0] == symb:
            # case of 'x > C'
            c_ = expr.args[1]
            if isinstance(c_, Integer):
                c_ = as_int(c_ + 1)
            else:  # Rational
                c_ = as_int(ceiling(c_))
            low = c_ if low is None else max(low, c_)
            return ((low, upp), S.true)
        elif expr.func == GreaterThan and expr.args[0] == symb:
            # case of 'x >= C'
            c_ = expr.args[1]
            if isinstance(c_, Integer):
                c_ = as_int(c_)
            else:  # Rational
                c_ = as_int(ceiling(c_))
            low = c_ if low is None else max(low, c_)
            return ((low, upp), S.true)
        elif expr.func == StrictLessThan and expr.args[0] == symb:
            # case of 'x < C'
            c_ = expr.args[1]
            if isinstance(c_, Integer):
                c_ = as_int(c_ - 1)
            else:  # Rational
                c_ = as_int(floor(c_))
            upp = c_ if upp is None else min(upp, c_)
            return ((low, upp), S.true)
        elif expr.func == LessThan and expr.args[0] == symb:
            # case of 'x <= C'
            c_ = expr.args[1]
            if isinstance(c_, Integer):
                c_ = as_int(c_)
            else:  # Rational
                c_ = as_int(floor(c_))
            upp = c_ if upp is None else min(upp, c_)
            return ((low, upp), S.true)
        elif expr.func == And:
            (b0, ass1) = self.calc_constraint(expr.args[0], bound, symb)
            (b1, ass2) = self.calc_constraint(expr.args[1], b0, symb)
            return (b1, ass1 & ass2)
        else:
            logger.warning("unsupported func: %s", expr.func)
            return (bound, expr)

    def gen_base(
        self,
        ast: Tree,
        context: CodeGenContext,
        constraint: Callable,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ) -> CodeGenResult:
        "generate a code for generating a value of base types."
        type_str = reconstruct(ast)
        match type_str:
            case 'int':
                _w = Dummy('w')
                _c = simplify(constraint(_w))
                logger.info("original constraint: %s", constraint)
                logger.info("simplified constraint: %s", _c)
                logger.info(srepr(_c))
                bound, assumption = self.calc_constraint(_c, (None, None), _w)
                logger.info((bound, assumption))
                l, u = bound

                def f():
                    v = rand_int(min_=l, max_=u)
                    if not constraint(v):
                        raise PyCheckAssumeError(
                            f'generated value {v} did not satisfy the assumption {constraint}')
                    return v
                return f, context
            case 'bool':
                return rand_bool, context
            case _:
                raise ValueError(f"unsupported base type: {type_str}")

    def gen_ref(
        self,
        ast: Tree,
        context: CodeGenContext,
        constraint: Callable,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ) -> CodeGenResult:
        "generate a code for generating a value of refinement types."
        base_var = str(ast.children[0].children[0].children[0].children[0])
        base_type = ast.children[0].children[1]
        predicate = ast.children[1]
        logger.info("var = %s", base_var)
        logger.info("base type = %s", base_type)
        logger.info("predicate = %s\n%s", reconstruct(predicate), predicate)

        # implementing...
        # eval_refinement(reconstruct(predicate), var)

        # old
        # def new_pred_func(x):
        #     return S(reconstruct(predicate)
        #              ).subs(symbols(var), x) & pred_func(x)

        logger.info('sympifying predicate...')
        predicate_s = S(reconstruct(predicate), locals={'is_sorted': IsSorted})
        logger.info(srepr(predicate_s))

        _x = Symbol(base_var)
        new_constraint = Lambda((_x,),
                                predicate_s & (constraint(_x)))
        logger.info(new_constraint)

        code, context = self.gen_gen(
            base_type, context=context, constraint=new_constraint)

        logger.info(code)

        return code, context

    def gen_prod(
        self,
        ast: Tree,
        context: CodeGenContext,
        constraint: Callable,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ) -> CodeGenResult:
        "generate a code for generating a value of product types."
        subtypes = []
        for ch in ast.children:
            if ch.data == "innertypedparam":  # childlen other than the last one
                logger.info("var = %s", ch.children[0])
                logger.info("type = %s", ch.children[1])
                subtypes.append(
                    (str(ch.children[0].children[0]), ch.children[1]))
            else:
                # probably the last element
                subtypes.append((None, ch))

        logger.info("subtypes:")
        for subtype in subtypes:
            logger.info(f"%s: %s", subtype[0], reconstruct(subtype[1]))
        # logger.info(pformat(subtypes))
        if len(subtypes) > 2:
            raise NotImplementedError(
                "currently n-tuple (where n > 2) is not supported")

        x1 = Symbol(subtypes[0][0])
        _x2 = Dummy('x2')
        _x3 = Dummy('x3')

        # codegen sigma(tau2)
        x2_tc_code, context = self.gen(
            subtypes[1][1], context=context, is_delta=True)
        logger.info(x2_tc_code)

        const2 = Lambda((_x2,), constraint((x1, _x2)))  # here x1 is free
        logger.info("const2 = %s", const2)
        const1 = Lambda((x1,), Exist(_x3, x2_tc_code(_x3) & const2(_x3)))
        logger.info("const1 = %s", const1)

        code1, context = self.gen_gen(
            subtypes[0][1], context=context, constraint=const1)

        def f():
            v1 = code1()
            code2, context = self.gen_gen(
                subtypes[1][1], context=context, constraint=const2(v1))
            v2 = code2()
            return (v1, v2)

        return f, context

    def gen_func(
        self,
        ast: Tree,
        context: CodeGenContext,
        constraint: Callable,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ) -> CodeGenResult:
        "generate a code for generating a value of product types."
        params = ast.children[0]

        if len(params.children) == 0:
            raise NotImplementedError(
                "currently 0-argument function (= thunk) is not supported")
        if len(params.children) > 1:
            raise NotImplementedError(
                "currently more than binary function is not supported")

        param = params.children[0]
        var = str(param.children[0].children[0])
        x_ = Symbol(var)
        var_type = param.children[1]
        return_type = ast.children[1]

        logger.info('---')
        # logger.info(param)
        logger.info("param name = %s", var)
        logger.info("param type = %s:\n%s", reconstruct(
            var_type), var_type.pretty())
        logger.info("return type = %s:\n%s", reconstruct(
            return_type), return_type.pretty())

        var_tc, context = self.gen(var_type, context=context)
        ret_gen, context = self.gen_gen(return_type, context=context)

        def f():
            return lambda x: ret_gen() if rand_bool() or var_tc(x) else PyCheckFailError

        return f, context

    def gen_list(
        self,
        ast: Tree,
        context: CodeGenContext,
        constraint: Callable,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ) -> CodeGenResult:
        "generate a code for generating a value of product types."
        type_ = ast.children[0]
        logger.info("element type = %s", type_)

        # logger.info("generating code for element type")
        # (element_type_code, context) = self.gen(
        #     ast=type_, context=context, is_delta=True
        # )
        # logger.info("generated code:\n%s", element_type_code)

        def gen(constr, idx):
            logger.info("gen constraint: %s", constr)

            def f():
                context = CodeGenContext()
                if rand_bool(p=0.25):
                    logger.info("** nil branch")
                    if constr(List()) != S.true:
                        raise PyCheckAssumeError(
                            f'generated value {[]} did not satisfy the assumption {constr}')
                    return []
                else:
                    logger.info("** cons branch")
                    z_ = ListSymbol(f'z{idx}')
                    logger.info(z_)
                    y_gen, context = self.gen_gen(
                        type_, constraint=true_func(), context=context)  # TODO
                    y = y_gen()
                    z = gen(Lambda((z_,), constr(Cons(y, z_))), idx+1)()
                    return [y] + z
            return f
        return gen(constraint, 0), context
