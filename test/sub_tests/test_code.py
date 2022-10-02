"test Code class."
from pycheck.codegen import Code


def test_fix_code():
    assert Code('x=3+y').fix_code().text == "x = 3+y\n"
    assert Code(
        'x=3+y').fix_code({'ignore': []}).text == "x = 3+y\n"
    assert Code('x=3 +y').fix_code().text == "x = 3 + y\n"
    assert Code('x=3 +y').fix_code({'ignore': []}).text == "x = 3 + y\n"
    assert Code('x=3*3+y*y').fix_code().text == "x = 3*3+y*y\n"
