"classes for types."
from collections.abc import Iterable
from dataclasses import dataclass, field

from lark import Token, Tree
from sympy import Basic, S, Symbol

from ..codegen.sympy_lib import IsSorted, Len, TupleSymbol
from ..parsing import TypeType, reconstruct


@dataclass
class PycheckType:
    "super class for parsed types."
    # iterable of variables that may occur free.
    # this will be used to handle dependent types.
    free_variables: Iterable[str] = field(kw_only=True)


@dataclass
class BaseType(PycheckType):
    "base types."
    type: str

    def __post_init__(self):
        if self.type not in ['int', 'bool']:
            raise NotImplementedError(
                f"successfully parsed but the type {self.type} is not supported yet")


@dataclass
class ProdType(PycheckType):
    "product types."
    first_var: str
    first_type: PycheckType
    second_type: PycheckType


@dataclass
class RefinementType(PycheckType):
    "refinement types."
    base_var: str
    base_type: PycheckType
    predicate: Basic
    predicate_free_variables: Iterable[str]


@dataclass
class ListType(PycheckType):
    "list types."
    base_type: PycheckType


@dataclass
class FunctionType(PycheckType):
    "function types."
    param_var: str
    param_type: PycheckType
    return_type: PycheckType


def get_type(ast: Tree, free_variables=None, strict=True) -> PycheckType:
    """
    get type object from parse tree.

    if strict is True, check is done for the restriction
        that pycheck currently supports.
    """
    assert isinstance(ast, Tree)
    if free_variables is None:
        free_variables = []

    match ast.data:
        case TypeType.BaseType.value:
            ch = ast.children[0]
            if isinstance(ch, Token):
                return BaseType(type=ch.value, free_variables=free_variables)
            else:
                assert ch.data == 'none'
                return BaseType(type=ch.children[0].value, free_variables=free_variables)
        case TypeType.ProductType.value:
            if strict and len(ast.children) != 2:
                raise NotImplementedError(
                    f"successfully parsed but the non-binary product is not supported yet")
            first = ast.children[0]
            first_var = first.children[0].children[0].value
            first_type = first.children[1]
            second_type = ast.children[1]

            return ProdType(
                first_var=first_var,
                first_type=get_type(
                    first_type, free_variables=free_variables),
                second_type=get_type(
                    second_type, free_variables=free_variables + [first_var]),
                free_variables=free_variables,
            )
        case TypeType.RefinementType.value:
            _locals = {'len': Len, 'is_sorted': IsSorted}

            main = ast.children[0]
            if strict and len(main.children) < 2:
                raise NotImplementedError(
                    f"successfully parsed but the rack of base variable is not supported yet")
            first_var = main.children[0].children[0].children[0].value

            first_type = main.children[1]
            base_type = get_type(first_type, free_variables=free_variables)
            if isinstance(base_type, ProdType):
                _locals[first_var] = TupleSymbol(first_var)

            predicate: Basic = S(reconstruct(
                ast.children[1]), locals=_locals)
            pred_free_var = free_variables + [first_var]

            # assertion of free variables in predicate
            _tmp = set(pred_free_var)  # TODO: avoid name duplication
            for symb in predicate.free_symbols:
                if strict and symb.name not in _tmp:
                    raise ValueError(
                        f"free variable scope is invalid. '{symb.name}' should not appear here")

            return RefinementType(
                base_var=first_var,
                base_type=base_type,
                predicate=predicate,
                predicate_free_variables=pred_free_var,
                free_variables=free_variables,
            )
        case TypeType.ListType.value:
            base_type = ast.children[0]
            return ListType(
                base_type=get_type(base_type, free_variables=free_variables), free_variables=free_variables,
            )
        case TypeType.FuncType.value:
            params = ast.children[0]
            ret_type = ast.children[1]

            if strict:
                if len(params.children) == 0:
                    raise NotImplementedError(
                        "successfully parsed but 0-argument function (= thunk) is not supported yet")
                if len(params.children) > 1:
                    raise NotImplementedError(
                        "successfully parsed but currently more than unary function is not supported yet")
                first_param = params.children[0]
                first_var = first_param.children[0].children[0].value
                first_type = first_param.children[1]
                return FunctionType(
                    param_var=first_var,
                    param_type=get_type(
                        first_type, free_variables=free_variables),
                    return_type=get_type(ret_type, free_variables=free_variables + [
                        first_var]),
                    free_variables=free_variables
                )
            else:
                raise Exception("not implemented yet")
        case _:
            raise ValueError(
                f"unknown top-level type '{ast.data}'")
