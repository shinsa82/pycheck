from mypy_examples.sato_rt import double_, fsum, main

from pycheck import check


def test_double():
    "normal (example based) test for double_()."
    assert double_(5) == 10


def succ(n: int) -> int:
    "used by test_fsum()."
    return n+1


def test_fsum():
    "normal (example based) test for fsum()."
    assert fsum(succ, 4) == succ(1)+succ(2)+succ(3)+succ(4)
    assert fsum(succ, 4) == (1+1)+(2+1)+(3+1)+(4+1)


def test_main():
    assert main(4) == double_(1) + double_(2)+double_(3)+double_(4)


def test_typecheck_main():
    assert check(main, max_iter=10)
