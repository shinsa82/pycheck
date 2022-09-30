"""legacy interfaces older than v0.3."""
import sys
from inspect import signature
from logging import getLogger
from operator import attrgetter
from random import normalvariate
from traceback import print_exc
from types import FunctionType, LambdaType

from hypothesis.strategies import text

debug, info = attrgetter('debug', 'info')(getLogger(__name__))
__version__ = '0.2'
MAX_TESTCASES = 100
NotImpl = 'not implemented yet.'


def valid_type(t) -> bool:
    info(f'valid_type: {t=}')
    if is_int(t) or is_str(t):
        return True
    if isinstance(t, dict):  # multiple argument type
        for k, tk in t.items():
            if not valid_type(tk):
                return False
        return True
    if isinstance(t, tuple):
        t0, p = t
        return (t0 is int) and callable(p)

    return False


def is_int(t):
    return t is int


def is_str(t):
    return t is str


def is_int_refined(t):
    if not isinstance(t, tuple):
        return None

    t0, p = t
    if (t0 is int) and callable(p):
        return p
    else:
        False


def rand_int():
    "generate a random int number."
    generated = int(normalvariate(0, 20))
    info(f'rand_int: {generated=}')
    return generated


def rand_str():
    "generate a random string."
    l = abs(rand_int())
    generated = text(min_size=l, max_size=l).example()
    info(f'rand_str: {generated=}')
    return generated


def rand_int_refined(p):
    "generate a random int number that satisfines the refinement."

    while True:
        generated = rand_int()
        if p(generated):
            break
        info(f'rand_int_refined: assume failed. {generated=}, {p=}')
        info('retrying generation...')
    return generated


def rand_funcargs(t):
    "generate a dict of multiple arguments."
    generated = {k: rand(tk) for k, tk in t.items()}
    info(f'rand_funcargs: {generated=}')
    return generated


def rand(t):
    "generate a value of type 't'."
    info(f'rand: {t=}')
    if is_int(t):
        return rand_int()
    if is_str(t):
        return rand_str()
    if isinstance(t, dict):  # multiple argument type
        return rand_funcargs(t)
    if p := is_int_refined(t):
        return rand_int_refined(p)
    raise NotImplementedError(f'no generator implemented for {t}.')


def beta(v, t):
    "beta function (type checking) for a pair of a value and a type."
    info(f'beta: {v=}, {t=}')
    assert valid_type(t), f'unsupported type: {t=}.'

    if is_int(t) or is_str(t):
        assert isinstance(v, t), f'type assertion failed: {v=}, {t=}'
    if p := is_int_refined(t):
        assert p(v), f'type assertion failed: {v=}, {t=}, {p=}.'


def beta_val(v, asserts):
    "beta function for value type terms."
    info(f'beta_val: {v=}, {asserts=}')
    assert asserts is int, NotImpl

    if is_int(asserts):
        assert isinstance(v, int), f'type assertion failed: {v=}, {asserts=}'

    return True


def beta_func(f, assumes, asserts):
    "beta function for function type terms."
    info(f'beta_func: {f=}, {assumes=}, {asserts=}')

    assert valid_type(assumes), f'unsupported type in assumes: {assumes}.'
    assert valid_type(asserts), f'unsupported type in asserts: {asserts}.'

    x = rand(assumes)
    info(f'generated func args: {x=}')

    # ad-hoc solution
    if isinstance(x, dict):
        res = f(**x)
    else:  # single argument
        res = f(x)
    info(f'result {res=}')
    beta(res, asserts)

    return True


def check_with_type(func, assumes, asserts) -> int:
    "entry point of type checking."
    info(f'check: {func=}, {assumes=}, {asserts=}')
    print('testing', end='')
    passed = 0

    try:
        while passed < MAX_TESTCASES:
            print('.', end='')
            beta_func(func, assumes, asserts)
            passed += 1
            info(f'{passed=}')
        print()
        print(f'{MAX_TESTCASES} testcases PASSED.')
        return 0
    except AssertionError:
        print('\ntest FAILED.')
        print_exc(file=sys.stdout)
        print('<show a falsifying example...>')
        return 1
