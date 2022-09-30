"""
Parser and utilities for type annnotations.

Copyright Notice: python3.lark is copied as is from the source code of lark.
"""
from inspect import signature
from logging import getLogger
from operator import attrgetter
from pathlib import Path
from pprint import pformat
from typing import Any

# from attr import dataclass
from environs import Env
from lark import Lark, Token, Transformer, Tree, v_args
from lark.tree import Meta

from ..type import (ArgsType, Base, FunctionType, Generic, RefinementType, Sum,
                    Type)
from ..type.normalization import complete, normalize

debug, info = attrgetter('debug', 'info')(getLogger(__name__))
_env = Env()
TYPESPEC_GRAMMAR = Path(__file__).parent / 'typespec.lark'

with _env.prefixed('PYCHECK_'):
    _debug = _env.bool('DEBUG_PARSER', False)
    info(f'set debug flag of typespec parser to {_debug}')
    # (dynamic) earley parser cannot use priorities on terminals,
    # which is used in common/python.lark.
    with open(TYPESPEC_GRAMMAR, mode='r') as f:
        typespec_parser: Lark = Lark(
            f,
            parser='earley',
            lexer='standard',
            debug=_debug,
            ambiguity='explicit',
            propagate_positions=True,
        )


def parse_typespec(typespec: str) -> Tree:
    """parse given typespec string and return constructed Tree."""
    return typespec_parser.parse(typespec)


class TypeSpecTransformer(Transformer):
    """Transformer that convers parsed Tree into a PyCheck type."""

    def __init__(self, text, globals_=None):
        "text: original text string"
        self.text = text
        if globals_:
            self.globals = globals_  # use given globals
        else:
            self.globals = locals()  # use this module's globals

    def text_(self, meta: Meta) -> str:
        "returns a substring of text that corresponds to positions in given Meta object."
        return self.text[meta.start_pos:meta.end_pos]

    def eval_text(self, s: str) -> Any:
        return eval(s, self.globals)

    def eval_(self, meta: Meta) -> Any:
        """
        returns an evaluated object that corresponding to positions in given Meta object.

        evaluation is performed with the current 'globals()' and 'locals()',
        which might be changed in future.
        """
        return eval(self.text_(meta), self.globals)

    @staticmethod
    def from_params(params: Tree) -> ArgsType:
        debug('params = ' + pformat(params, sort_dicts=False))
        debug(params.children)
        return ArgsType(params=params.children)

    @v_args(inline=True, meta=True)
    def none(self, meta: Meta, type_name: Token):
        "None and NoneType as type spec are converted to 'None'."
        debug('-- none --')
        assert isinstance(type_name, Token)
        assert isinstance(meta, Meta)
        debug(repr(type_name))
        debug(f'text = {self.text_(meta)}')
        o = Base(type_name='None', type_=None)
        debug(f'evaluated to {o}')
        return o

    @v_args(inline=True, meta=True)
    def base(self, meta: Meta, type_name: Token):
        debug('-- base --')
        assert isinstance(type_name, Token)
        assert isinstance(meta, Meta)
        debug(repr(type_name))
        type_name = self.text_(meta)
        debug(f'text = {type_name}')
        o = Base(type_name=type_name, type_=self.eval_text(type_name))
        debug(f'evaluated to {o}')
        return o

    @v_args(inline=True, meta=True)
    def generic(self, meta: Meta, head_type: Tree, type_args: Tree):
        debug('-- generics --')
        assert isinstance(type_args, Tree)
        assert isinstance(meta, Meta)
        debug(repr(head_type))
        debug(repr(type_args))
        type_name = self.text_(meta)
        debug(f'text = {type_name}')
        o = Generic(type_name=type_name, type_=self.eval_text(type_name))
        debug(f'evaluated to {o}')
        return o

    @v_args(inline=True, meta=True)
    def sum_type(self, meta: Meta, *types: tuple):
        debug('-- sum type --')
        assert isinstance(types, tuple)
        assert isinstance(meta, Meta)
        debug(repr(types))
        type_name = self.text_(meta)
        debug(f'text = {type_name}')
        # Generic(type_name=type_name, type_=self.eval_text(type_name))
        o = Sum(
            type_name=type_name,
            dirty=True,
            type_=None,  # type_=Union[types],
            choices=list(types)
        )
        debug(f'evaluated to {o}')
        return o

    @v_args(inline=True, meta=True)
    def typedparam(self, meta: Meta, var: Token, type_: Type):
        debug('-- typedparam --')
        debug(repr(var))
        debug(repr(type_))
        assert isinstance(var, Token)
        assert isinstance(type_, Type)
        assert isinstance(meta, Meta)
        type_name = self.text_(meta)
        debug(f'text = {type_name}')
        o = (var.value, type_)
        debug(f'evaluated to {o}')
        return o

    @v_args(inline=True, meta=True)
    def func_type(self, meta: Meta, params: Tree, ret_type: Type):
        debug('-- func type --')
        debug(repr(params))
        debug(repr(ret_type))
        assert isinstance(params, Tree)
        assert params.data in ['params', 'params_plus']
        assert isinstance(ret_type, Type)
        assert isinstance(meta, Meta)
        type_name = self.text_(meta)
        debug(f'text = {type_name}')
        o = FunctionType(
            args_type=self.from_params(params),
            return_type=ret_type,
            type_name=type_name,
            type_=None,  # self.eval_text(type_name)
            dirty=True
        )
        debug(f'evaluated to {o}')
        return o

    @v_args(inline=True, meta=True)
    def var_decl(self, meta: Meta, var_name: Token = None) -> str:
        debug('-- var_decl --')
        debug(pformat(var_name))
        if var_name is None:
            return ''
        else:
            debug(var_name.value)
            return var_name.value

    @v_args(inline=True, meta=True)
    def ref_type(self, meta: Meta, var: str, type_: Type, pred: Tree):
        debug('-- ref_type --')
        debug(f'base_var = {var!r}')
        debug(f'base type = {type_!r}')
        debug(f'predicate = {pred!r}')
        assert isinstance(var, str)
        assert isinstance(type_, Type)
        assert isinstance(pred, Tree)
        assert isinstance(meta, Meta)
        type_name = self.text_(meta)
        debug(f'type text = {type_name}')
        o = RefinementType(
            base_var=var,
            base_type=type_,
            type_name=type_name,
            predicate=self.eval_(pred.meta),
            type_=None,  # self.eval_text(type_name)
            dirty=True
        )
        o.signature = signature(o.predicate)
        debug(f'evaluated to {o}')
        return o


def gen_typespec(tree: Tree, text: str, globals_: Any = None) -> Type:
    """construct a typespec object (used inside PyCheck) from parsed Tree."""
    return TypeSpecTransformer(text=text, globals_=globals_).transform(tree)


def parse(typespec: str, globals_: Any = None, post_process=True) -> Type:
    "parse a typespec string and construct a typespec object."
    t: Tree = parse_typespec(typespec)
    debug(f'typespec tree:\n' + t.pretty())
    raw = gen_typespec(tree=t, text=typespec, globals_=globals_)
    return (normalize(complete(raw)) if post_process else raw)
