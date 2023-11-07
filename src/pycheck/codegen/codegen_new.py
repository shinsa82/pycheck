"new version of codegen."
from logging import getLogger
from pprint import pformat
from time import perf_counter
from typing import Callable

from lark import Tree
from sympy import (ITE, And, Dummy, Function, GreaterThan, Integer, Lambda,
                   LessThan, Rational, S, StrictGreaterThan, StrictLessThan,
                   Symbol, ceiling, floor, simplify, srepr)
from sympy.utilities.misc import as_int

from ..const import PyCheckAssumeError, PyCheckFailError
from ..parsing import reconstruct as _recon
from ..random.random_generators import rand_bool, rand_int
from ..types import BaseType, FunctionType, ListType, ProdType, RefinementType, PycheckType
# from .codegen_base import CodeGenBase
from .const import CodeGenContext, CodeGenResult, true_func
from .sympy_lib import (All, Cons, Exist, IsSorted, Len, List, ListSymbol, Map,
                        TupleSymbol)

logger = getLogger(__name__)


def reconstruct(typ: PycheckType) -> str:
    "string reconstruction for PycheckType."
    return _recon(typ.ast)


def tc_base(
    self: BaseType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to process options # pylint: disable=unused-argument
):
    "generate a code for typechecking the term with base types."
    logger.debug("[typecheck base]")
    logger.debug("type = %s", self)
    return Lambda((Dummy('x'),), S.true), context


def tc_ref(
    self: RefinementType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to process options # pylint: disable=unused-argument
):
    "generate a code for typechecking the term with refinement types."
    logger.debug("[typecheck ref]")
    logger.debug("var = %s", self.base_var)
    logger.debug("type = %s", self.base_type)
    logger.debug("predicate = %s", self.predicate)

    logger.debug("generating TC code for %s against main type %s",
                 self.base_var, self.base_type)
    (main_type_code, context) = self.base_type.gen(
        context=context, is_delta=True)
    logger.debug("TC code for main (refinement) type:\n%s", main_type_code)

    logger.debug("generating main code with predicate")
    _x = Symbol(self.base_var)
    body = main_type_code(_x) & self.predicate
    logger.debug('main code function body = %s', body)

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
    logger.debug("[typecheck list]")
    logger.debug("element type = %s", self.base_type)

    logger.info("generating code for element type")
    (element_type_code, context) = self.base_type.gen(
        context=context, is_delta=True
    )
    logger.info("generated code:\n%s", element_type_code)

    logger.info("generating TC main code for list")
    _x = ListSymbol(f'x{context.get_vsuf()}')
    return Lambda((_x,), All(Map(element_type_code, _x))), context


def tc_prod(
    self: ProdType,
    context: CodeGenContext,
    is_delta: bool = False,
    **kwargs  # to ignore 'value' param # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for typechecking the term with product types."
    logger.debug("[typecheck prod]")
    logger.debug("var = %s", self.first_var)
    logger.debug("type = %s", self.first_type)
    logger.debug("second = %s", self.second_type)

    first_type_code, context = self.first_type.gen(context, is_delta=True)
    logger.debug(first_type_code)
    second_type_code, context = self.second_type.gen(context, is_delta=True)
    _y = Symbol(self.first_var)
    _x = TupleSymbol(f'x{context.get_vsuf()}')
    second_type_code = Lambda(_y, second_type_code)
    logger.debug(second_type_code)
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

    logger.debug(self.param_var)
    logger.debug("param type = %s", self.param_type)
    logger.debug("return type = %s", self.return_type)

    gen_code, context = self.param_type.gen_gen(
        context=context, constraint=Lambda((Dummy('x'),), S.true))

    tc_code, context = self.return_type.gen(context=context, is_delta=False)

    def ret(f):
        v = gen_code(env=None)()
        logger.debug("generated v = %s", v)
        r = f(v)
        logger.debug("returned r = %s", r)
        return tc_code(r).subs(x_, v)

    # ret = Lambda((_f,), tc_code(_f(gen_code())))
    logger.debug(ret)
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
        logger.debug("unsupported func: %s", expr.func)
        return (bound, Lambda((symb,), expr))


def gen_base(
    self: BaseType,
    context: CodeGenContext,
    constraint: Callable,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for generating a value of base types."
    logger.debug("[gen base]")
    logger.debug("type = %s", self.type)
    logger.debug("constraint = %s", constraint)
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
                    _start = perf_counter()
                    _c = simplify(constraint(_w))
                    _end = perf_counter()
                    logger.debug("original constraint: %s", constraint)
                    logger.debug("simplified constraint: %s", _c)
                    logger.debug("-> simplification: %f ms",
                                 (_end-_start) * 1000.0)
                    logger.debug(srepr(_c))
                    bound, assumption = calc_constraint(_c, (None, None), _w)
                    logger.debug(f"bound = {bound}")
                    logger.debug(f"assumption = {assumption}")
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
    logger.debug("[gen ref]")
    logger.debug("var = %s (%s)", self.base_var, type(self.base_var))
    logger.debug("base type = %s", self.base_type)
    logger.debug("predicate = %s (%s)", self.predicate, srepr(self.predicate))

    # implementing...
    # eval_refinement(reconstruct(predicate), var)

    # old
    # def new_pred_func(x):
    #     return S(reconstruct(predicate)
    #              ).subs(symbols(var), x) & pred_func(x)

    if isinstance(self.base_type, ProdType):
        _x = TupleSymbol(self.base_var)
    elif isinstance(self.base_type, ListType):
        _x = ListSymbol(self.base_var)
    else:
        _x = Symbol(self.base_var)
    new_constraint = Lambda((_x,),
                            self.predicate.subs(Symbol(self.base_var), _x) & (constraint(_x)))
    logger.debug(f"new constraint = %s (%s)",
                 new_constraint, srepr(new_constraint))

    code, context = self.base_type.gen_gen(
        context=context, constraint=new_constraint)

    logger.debug(code)

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
    logger.debug("[gen prod]")

    subtypes = []

    logger.debug(f"type = {reconstruct(self)}")
    logger.debug("first var = %s", self.first_var)
    logger.debug("first type = %s", self.first_type)
    logger.debug("second type = %s", self.second_type)

    # subtypes = [(self.first_var, self.first_type), (None, self.second_type)]
    x1 = Symbol(self.first_var)
    _x2 = Dummy('x2')
    _x3 = Dummy('x3')

    # codegen sigma(tau2)
    logger.debug("generation for the second type...")
    x2_tc_code, context = self.second_type.gen(
        context=context, is_delta=True)
    logger.debug(x2_tc_code)

    const2 = Lambda((_x2,), constraint((x1, _x2)))  # here x1 is free
    logger.debug("const2 = %s", const2)
    const1 = Lambda((x1,), Exist(_x3, x2_tc_code(_x3) & const2(_x3)))
    logger.debug("const1 = %s", const1)

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
    logger.debug("[gen func]")

    var = self.param_var
    x_ = Symbol(var)
    var_type = self.param_type
    return_type = self.return_type

    logger.info('---')
    # logger.info(param)
    logger.info("param name = %s", var)
    logger.info("param type = %s:\n%s", reconstruct(
        var_type), var_type)
    logger.info("return type = %s:\n%s", reconstruct(
        return_type), return_type)

    var_tc, context = var_type.gen(context=context)
    ret_gen, context = return_type.gen_gen(constraint=true_func(), context=context)

    def f():
        return lambda x: ret_gen() if rand_bool() or var_tc(x) else PyCheckFailError

    return f, context


def gen_inner(typ, constraint, context, delta_exp, idx=1):
    """
    'gen' function in my paper, used within gen_list().

    Here typ should be a ListType.
    """
    def _outer(env=None):
        env = env or {}  # bound env in this closure

        def _():
            logger.debug("[gen_inner]")
            logger.debug("list generation(%d): start", idx)
            start = perf_counter()
            assert isinstance(typ, ListType)

            logger.debug("type = %s", reconstruct(typ))
            logger.debug("constraint = %s", constraint)
            logger.debug("  constraint (srepr): %s", srepr(constraint))

            logger.debug("choosing nil/cons...")
            if rand_bool(p=0.25):
                logger.debug("nil branch selected")
                logger.debug("generated = %s", [])
                ph_nil = constraint(List())
                logger.debug("ψ(nil) = %s", ph_nil)
                if ph_nil != S.true:
                    raise PyCheckAssumeError(
                        f'generated value {[]} did not satisfy the assumption {constraint}')
                end = perf_counter()
                logger.debug("list generation (%d): %f ms",
                             idx, (end-start)*1000.0)
                return []
            else:
                logger.debug("cons branch selected")
                y_ = Symbol(context.var('y'))
                z_ = ListSymbol(context.var('z'))
                p1 = constraint(Cons(y_, z_))
                logger.debug("ψ(cons %s %s) = %s", y_, z_, p1)
                # z_tc_code, _context = typ.gen(
                #     context=context, is_delta=True)
                logger.debug(f"list type TC code = {delta_exp}")
                exist_clause = Exist(
                    z_, delta_exp(z_) & constraint(Cons(y_, z_)).subs(env))
                logger.debug("∃z clause = %s", exist_clause)
                _constraint = Lambda((y_,), exist_clause)
                logger.debug(f"constraint for y = {_constraint}")

                y_gen, _context = typ.base_type.gen_gen(
                    constraint=_constraint, context=context)  # TODO
                y = y_gen(env)()
                logger.debug(f"generated y = {y}")
                z = gen_inner(
                    typ,
                    constraint=Lambda((z_,), constraint(Cons(y, z_))),
                    context=_context,
                    idx=idx+1,
                    delta_exp=delta_exp,
                    # env=env | {y_: y}
                )(env | {y_: y})()
                logger.debug(f"generated z = {z}")
                end = perf_counter()
                logger.debug("list generation(%d): %f ms",
                             idx, (end-start)*1000.0)
                return [y] + z

        return _

    return _outer


def gen_list(
    self: ListType,
    context: CodeGenContext,
    constraint: Callable,
    **kwargs  # to process options # pylint: disable=unused-argument
) -> CodeGenResult:
    "generate a code for generating a value of product types."
    logger.debug("[gen list]")
    type_ = self.base_type
    logger.debug("  element type = %s", reconstruct(type_))
    logger.debug("  constraint: %s", constraint)
    logger.debug("  constraint (srepr): %s", srepr(constraint))

    logger.debug("---- pre computation exp ----")
    logger.debug("ψ(nil) = %s", constraint(List()))
    y_ = Symbol(context.var('y'))
    z_ = ListSymbol(context.var('z'))
    p1 = constraint(Cons(y_, z_))
    logger.debug("ψ(cons %s %s) = %s", y_, z_, p1)
    delta, context = self.gen(context=context, is_delta=True)
    logger.debug("δ(%s)(%s) = %s", reconstruct(self), z_, delta(z_))
    # logger.debug("∃z clause = %s", Exist(
    #     (z_,), delta(z_) & constraint(Cons(y_, z_))))
    logger.debug("==== pre computation exp ====")

    return gen_inner(self, constraint, context, delta_exp=delta), context


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
