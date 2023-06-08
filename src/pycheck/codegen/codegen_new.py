"new version of codegen."
from logging import getLogger
from pprint import pformat
from typing import Callable

from lark import Tree
from sympy import (And, Dummy, Function, GreaterThan, Lambda, LessThan, S,
                   StrictGreaterThan, StrictLessThan, Symbol, simplify)

from ..const import PyCheckAssumeError
from ..parsing import reconstruct
from ..random.random_generators import rand_bool, rand_int
from .codegen_base import CodeGenBase
from .const import CodeGenContext, CodeGenResult
from .sympy_lib import All, Exist, Len, ListSymbol, Map, TupleSymbol

logger = getLogger(__name__)


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
                # 'list_type': self.gen_list,
                'ref_type': self.gen_ref,
                'prod_type': self.gen_prod,
                # 'func_type': self.gen_func,
            }
        )

    def tc_base(
        self,
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ):
        "generate a code for typechecking the term with base types."
        return Lambda((Dummy('x'),), S.true), context

    def tc_ref(
        self,
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ):
        "generate a code for typechecking the term with refinement types."
        var = ast.children[0].children[0].children[0]
        type_ = ast.children[0].children[1]
        predicate = ast.children[1]
        logger.debug("var = %s", (str(var.children[0]), var))
        logger.debug("type = %s", type_)
        logger.info("predicate = (%s)\n%s", reconstruct(predicate), predicate)

        logger.info("generating code for main type")
        (main_type_code, context) = self.gen(
            ast=type_, context=context, is_delta=True)
        logger.info("code for main type:\n%s", main_type_code)

        logger.info("generating main code with predicate")
        param = str(var.children[0])

        _x = Symbol(param)
        S_predicate = S(reconstruct(predicate), locals={'len': Len})
        logger.info('predicate in SymPy = %s', S_predicate)
        body = main_type_code(_x) & S_predicate
        logger.info('main code function body = %s', body)
        # logger.info('**DEBUG**: %s', body.subs(_x, List(1,2,3)))
        # logger.info('**DEBUG**: %s', body.subs(_x, List()))

        # causes an error when Len(l) is used
        # so move simplify later, into gen method.
        # lam_body = simplify(body)
        return Lambda(_x, body), context

    def tc_list(
        self,
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ):
        "generate a code for typechecking the term with list types."
        type_ = ast.children[0]
        logger.debug("element type = %s", type_)

        logger.info("generating code for element type")
        (element_type_code, context) = self.gen(
            ast=type_, context=context, is_delta=True
        )
        logger.info("generated code:\n%s", element_type_code)

        logger.info("generating main code")
        # entry_point, param, context = gen_header_elements(context)
        # body = f"return all(map({element_type_code.entry_point},{param}))"
        # logger.info(body)

        # generated = code_func(code_func_header(entry_point, [
        #     param]), element_type_code.text + body)
        # return (Code(generated, entry_point=entry_point).fix_code(), context)

        _x = ListSymbol(f'x{context.get_vsuf()}')
        # TODO: add `all`
        return Lambda(_x, All(Map(element_type_code, _x))), context

    def tc_prod(
        self,
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False,
        **kwargs  # to ignore 'value' param # pylint: disable=unused-argument
    ) -> CodeGenResult:
        "generate a code for typechecking the term with product types."
        # currently only binary tuples (= pairs) are supported.
        assert len(
            ast.children) == 2, "currently only the pair (= binary tuple) is supported"

        ch = ast.children
        first_var = str(ch[0].children[0].children[0])
        first_type = ch[0].children[1]
        second_type = ch[1]
        logger.info("var = %s", first_var)
        logger.info("type = %s\n%s", reconstruct(
            first_type), first_type.pretty())
        logger.info("second = \n%s", second_type.pretty())

        first_type_code, context = self.gen(first_type, context, is_delta=True)
        logger.info(first_type_code)
        second_type_code, context = self.gen(
            second_type, context, is_delta=True)
        _y = Symbol(first_var)
        _x = TupleSymbol(f'x{context.get_vsuf()}')
        second_type_code = Lambda(_y, second_type_code)
        logger.info(second_type_code)
        ret = Lambda((_x,), first_type_code(
            _x[0]) & second_type_code(_x[0])(_x[1]))
        logger.info(ret)
        return ret, context

    def tc_func(
        self,
        ast: Tree,
        context: CodeGenContext,
        is_delta: bool = False,
        **kwargs  # to process options # pylint: disable=unused-argument
    ) -> CodeGenResult:
        "generate a code for typechecking the term with function types."
        if is_delta:
            # return identity func
            return Lambda(Dummy('x'), S.true), context

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

        logger.info(param)
        logger.info(var)
        logger.info("param type = %s:\n%s", reconstruct(
            var_type), var_type.pretty())
        logger.info("return type = %s:\n%s", reconstruct(
            return_type), return_type.pretty())

        _f = Function(var)

        gen_code, context = self.gen_gen(
            var_type, context=context, constraint=Lambda((Dummy('x'),), S.true))

        tc_code, context = self.gen(return_type, context=context)

        def ret(f):
            v = gen_code()
            logger.info("v = %s", v)
            r = f(v)
            logger.info("r = %s", r)
            return tc_code(r).subs(x_, v)
            # return tc_code(r)
        # ret = Lambda((_f,), tc_code(_f(gen_code())))
        logger.info(ret)
        return ret, context

    def calc_constraint(self, expr, bound, symb) -> tuple[tuple[int, int], str]:
        """
        returns integer bound (inclusive). None means infinity.

        symb is a free variable in expr.
        """
        # logger.info("%s: %s", expr, srepr(expr))
        low, upp = bound

        # TODO bound update is not complete.
        if expr == S.true:  # it's correct; do not fix.
            return (bound, S.true)
        elif expr.func == StrictGreaterThan and expr.args[0] == symb:
            # case of 'x > C'
            low = expr.args[1] + \
                1 if low is None else max(low, expr.args[1] + 1)
            return ((low, upp), S.true)
        elif expr.func == GreaterThan and expr.args[0] == symb:
            # case of 'x >= C'
            low = expr.args[1] if low is None else max(low, expr.args[1])
            return ((low, upp), S.true)
        elif expr.func == StrictLessThan and expr.args[0] == symb:
            # case of 'x < C'
            upp = expr.args[1] - \
                1 if upp is None else min(upp, expr.args[1] - 1)
            return ((low, upp), S.true)
        elif expr.func == LessThan and expr.args[0] == symb:
            # case of 'x <= C'
            upp = expr.args[1] if upp is None else min(upp, expr.args[1])
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
                bound, assumption = self.calc_constraint(_c, (None, None), _w)
                logger.info((bound, assumption))
                l, u = bound

                def f():
                    v = rand_int(min_=l, max_=u)
                    if not constraint(v):
                        raise PyCheckAssumeError(
                            f'generated value {v} did not satisfy the assumption')
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

        _x = Symbol(base_var)
        new_constraint = Lambda(
            (_x,), S(reconstruct(predicate)) & (constraint(_x)))
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

        logger.info(pformat(subtypes))
        if len(subtypes) > 2:
            raise NotImplementedError(
                "currently n-tuple (where n > 2) is not supported")

        x1 = Symbol(subtypes[0][0])
        _x2 = Dummy('x2')
        _x3 = Dummy('x3')
        x2_tc_code, context = self.gen(
            subtypes[1][1], context=context, is_delta=True)
        logger.info(x2_tc_code)
        const2 = Lambda((_x2,), constraint((x1, _x2)))
        logger.info("const2 = %s", const2)
        const1 = Lambda((x1,), Exist(_x3, x2_tc_code(_x3) & const2(_x3)))
        logger.info("const1 = %s", const1)

        code1, context = self.gen_gen(
            subtypes[0][1], context=context, constraint=const1)
        code2, context = self.gen_gen(
            subtypes[1][1], context=context, constraint=const2)

        def f():
            v1 = code1()
            v2 = code2()
            return (v1, v2)
        return f, context  # TODO: add