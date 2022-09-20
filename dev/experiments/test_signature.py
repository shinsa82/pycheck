from inspect import Signature, isbuiltin, signature
from types import BuiltinFunctionType

import pytest

raises = pytest.raises
xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


builtin_classes_and_others = [bool,
                              bytearray,
                              bytes,
                              classmethod,
                              complex,
                              dict,
                              enumerate,
                              filter,
                              float,
                              frozenset,
                              help,
                              int,
                              list,
                              map,
                              memoryview,
                              object,
                              property,
                              range,
                              reversed,
                              set, slice, staticmethod,
                              str, super,
                              tuple,
                              type,
                              zip]


@parametrize('obj', builtin_classes_and_others)
def test_isbuiltin_fails_for_builin_classes(obj):
    print(type(obj))
    assert not isbuiltin(obj)


builtin_funcs = [
    abs,
    all,
    any,
    ascii,
    bin,
    breakpoint,
    callable,
    chr,
    compile,
    delattr,
    dir,
    divmod,
    eval,
    exec,
    format,
    getattr,
    globals,
    hasattr,
    hash,
    hex,
    id,
    input,
    isinstance,
    issubclass,
    iter,
    len,
    locals,
    max,
    min,
    next,
    oct,
    open,
    ord,
    pow,
    print,
    repr,
    round,
    setattr,
    sorted,
    sum,
    vars
]

builtin_funcs_with_sig = [
    abs,
    all,
    any,
    ascii,
    bin,
    callable,
    chr,
    compile,
    delattr,
    divmod,
    eval,
    exec,
    format,
    globals,
    hasattr,
    hash,
    hex,
    id,
    input,
    isinstance,
    issubclass,
    len,
    locals,
    oct,
    open,
    ord,
    pow,
    repr,
    round,
    setattr,
    sorted,
    sum
]

builtin_funcs_without_sig = [
    breakpoint,
    dir,
    getattr,
    iter,
    max,
    min,
    next,
    print,
    vars
]


@parametrize('obj', builtin_funcs)
def test_isbuiltin_works_for_these(obj):
    assert isbuiltin(obj)
    assert isinstance(obj, BuiltinFunctionType)


@parametrize('obj', builtin_funcs_with_sig)
def test_signature_works_for_these(obj):
    assert signature(obj) is not None
    print(obj, signature(obj))


@parametrize('obj', builtin_funcs_without_sig)
def test_signature_fails_for_these(obj):
    with raises(ValueError):
        signature(obj)


def test_signature_fails_for_int():
    with raises(TypeError):
        signature(3)


def test_signature_succeeds_for_functions():
    def foo(x: int, y: int) -> int:
        return x - y

    print(foo, signature(foo))
    assert isinstance(signature(foo), Signature)


def test_signature_succeeds_for_lambdas():
    print(signature(lambda x, y: x - y))
