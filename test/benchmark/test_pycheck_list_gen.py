# naive list generation, for interim report
from time import perf_counter

from pandas import Series
from rich import print
from sympy import Dummy, Lambda, S, Symbol, Tuple, true

from pycheck import RefType, code_gen
from pycheck.codegen.sympy_lib import IsSorted, ListSymbol
from pycheck.random.random_generators import rand_bool, rand_int


def true_func():
    "get new True constant function, 'lambda x: true', with a fresh variable."
    return Lambda((Dummy('x'),), S.true)


def generator():
    code = code_gen(reftype=RefType(
        "{ l:list[int] | is_sorted(l) }", strict=False), mode="gen", constraint=true_func())
    return code


def pred_ascending(l: list) -> bool:
    return Series(l).is_monotonic_increasing


def pred_ascending_long(l: list) -> bool:
    return len(l) >= 3 and Series(l).is_monotonic_increasing


def _test_sub(pred, show_valid_only=False):
    print("")
    if show_valid_only:
        print("[yellow]WARN: Show only values that satisfy the property.[/]")
    gen = generator()
    naive_gen_time = []
    gen_time = []

    retry = 0
    for _ in range(10):
        s0 = perf_counter()
        while True:
            s1 = perf_counter()
            l = gen()()
            s2 = perf_counter()
            naive_gen_time.append(s2-s1)
            if pred(l):
                print(f"{pred(l)} {l}")
                break
            if not show_valid_only:
                print(f"{pred(l)} {l}")
            retry += 1
        s3 = perf_counter()
        gen_time.append(s3-s0)

    print(f"{retry=}")
    print(
        f"avg. generation time (each): { sum(naive_gen_time)*1000 / len(naive_gen_time) } ms")
    print(
        f"avg. generation time (valid): { sum(gen_time)*1000 / len(gen_time) } ms")
    # print(naive_gen_time)


def test_gen_1():
    _test_sub(pred_ascending)


# def test_gen_2():
#     _test_sub(pred_ascending_long, show_valid_only=True)
