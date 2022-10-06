"test Code class."
from pycheck.codegen import Code


def test_fix_code():
    assert Code('x=3+y').fix_code().text == "x = 3+y\n"
    assert Code(
        'x=3+y').fix_code({'ignore': []}).text == "x = 3+y\n"
    assert Code('x=3 +y').fix_code().text == "x = 3 + y\n"
    assert Code('x=3 +y').fix_code({'ignore': []}).text == "x = 3 + y\n"
    assert Code('x=3*3+y*y').fix_code().text == "x = 3*3+y*y\n"

    assert Code(
        'def f(x):\n  return x+1').fix_code().text == "def f(x):\n    return x+1\n"
    assert Code(
        'def f(x):\n  def g(y):\n    return y+1\n  return g(x)+1').fix_code().text == \
        'def f(x):\n    def g(y):\n        return y+1\n    return g(x)+1\n'
