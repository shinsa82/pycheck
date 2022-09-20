"entrypoint of tests for generator module"
from inspect import getsource
from logging import info

import pytest
from pycheck.generator import (BoolType, CharType, DataFrameType, FloatType,
                               FuncType, IntType, ListType, ProdType, RefType,
                               StringType, sigma)

_base_classes = {IntType, BoolType, FloatType, CharType}
_other_classes = {ListType, StringType,
                  DataFrameType, FuncType, ProdType, RefType}
_classes = _base_classes | _other_classes


@pytest.mark.parametrize('cls', _classes)
def test_types_ctor(cls):
    "instantiation check of Types."
    _ = cls()


@pytest.mark.parametrize('cls', _base_classes)
def test_sigma_base(cls):
    "invoking sigma() with BaseTypes."
    f = sigma(cls())
    assert f is not None


def test_sigma_int():
    "invoking sigma() with IntType."
    f_str = sigma(IntType())
    info(f_str)
    f = eval(f_str)
    assert f(3)
    assert not f(True)


def test_sigma_bool():
    "invoking sigma() with BoolType."
    f_str = sigma(BoolType())
    info(f_str)
    f = eval(f_str)
    assert f(True)
    assert not f(3)
    assert not f(1)


def test_sigma_float():
    "invoking sigma() with FloatType."
    f_str = sigma(FloatType())
    info(f_str)
    f = eval(f_str)
    assert f(3.14)
    assert not f(1)
    assert not f(False)


def test_sigma_char():
    "invoking sigma() with CharType."
    f_str = sigma(CharType())
    info(f_str)
    f = eval(f_str)
    assert f("3")
    assert not f(3)
    assert not f("test")
    assert not f(True)


@pytest.mark.xfail
@pytest.mark.parametrize('cls', _other_classes)
def test_sigma_other(cls):
    "invoking sigma() with other types."
    sigma(cls())


def test_sigma_ref():
    "invoking sigma() with RefType."
    f_str = sigma(RefType('y', IntType(), lambda v: f"{v} > 0"))
    info(f_str)
    f = eval(f_str)
    assert f(3)
    assert not f(0)
    assert not f("bad")
