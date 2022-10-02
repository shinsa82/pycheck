from inspect import signature
from pprint import pprint

from more_itertools import is_sorted  # used by pick_min() below
from pandas import DataFrame
from pycheck import check, spec
from pycheck.spec import TypeSpec, has_typespec, typespec
from pycheck.type import ArgsType, FunctionType, SignatureFunctionType, args
from pytest import mark


def inc(y: int, x: int) -> int:
    return x + y + 1


# @spec(args(x=int, y=int) >> int)
@spec('(y:int, x:int) -> int')
def inc_decorated(y: int, x: int) -> int:
    "sample decorated function (inc)."
    return x + y + 1


@spec('df:DataFrame -> int', eager=True)
def dataframe_size(df: DataFrame) -> int:
    "sample decorated function (size). specifies eager evaluation of typespec."
    return df.size


def test_spec_does_not_change_signature():
    assert signature(inc) == signature(inc_decorated)
    assert inc_decorated(3, 4) == 8


def test_typespec_func():
    ts1 = inc_decorated.__pycheck_spec__
    ts2 = typespec(inc_decorated, raw=True)
    assert ts1 is ts2
    a1 = inc_decorated.__pycheck_spec__.ast
    a2 = typespec(inc_decorated)
    assert a1 is a2


def test_spec_prop_exists_within_decorated():
    assert hasattr(inc_decorated, "__pycheck_spec__")
    spec_obj: TypeSpec = getattr(inc_decorated, "__pycheck_spec__")
    assert not spec_obj.check_args
    assert not spec_obj.check_ret
    assert has_typespec(inc_decorated)


def test_spec_correctly_preserved():
    t = typespec(inc_decorated)
    assert isinstance(t, FunctionType)
    # assert t.raw_args_type.args_type == {"x": int, "y": int}
    assert isinstance(t.args_type, ArgsType)
    at: ArgsType = t.args_type
    assert list(at.args_type.keys()) == ['y', 'x']  # order is preserved?
    assert t.return_type.type_ == int


@spec('l: { m:list[int] | lambda m: len(m)>0 and is_sorted(m) } -> int')
def pick_min(l: list[int]) -> int:
    "test target func."
    return l[0]


def test_list() -> None:
    "test list type spec."
    pprint(typespec(pick_min))

# @mark.skip(reason='deprecated test')
# def test_ArgsType():
#     t = ArgsType(x=int, y=int)
#     assert t.args_type == {"x": int, "y": int}


# @mark.skip(reason='deprecated test')
# def test_args():
#     t = args(x=int, y=int)
#     assert t.args_type == {"x": int, "y": int}


# @mark.skip(reason='deprecated test')
# def test_ArgsType_rshift():
#     t_args = ArgsType(x=int, y=int)
#     t_func = t_args >> int
#     assert isinstance(t_func, FunctionType)
#     assert t_func.raw_args_type == t_args
#     assert t_func.return_type == int


# @mark.skip(reason='deprecated test')
# def test_get_signature():
#     sig = typespec(inc)
#     assert isinstance(sig, SignatureFunctionType)
#     assert sig.args_type == {"x": int, "y": int}
#     assert sig.return_type == int


# @mark.skip(reason='deprecated test')
# def test_get_signature_decorated():
#     sig = typespec(inc_decorated)
#     assert isinstance(sig, FunctionType)
#     assert sig.args_type == {"x": int, "y": int}
#     assert sig.return_type == int
