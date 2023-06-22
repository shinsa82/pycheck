"test Code and gen_helper modules."
from pycheck.codegen import Code
from pycheck.codegen.const import CodeGenContext
from pycheck.codegen.code_builder import CodeBuilder


def test_context():
    "test codegen context."
    context = CodeGenContext()
    assert context.func_suffix == 0
    assert context.var_suffix == 0
    assert context.get_fsuf() == 0
    assert context.get_vsuf() == 0
    assert context.func_suffix == 1
    assert context.var_suffix == 1


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


def test_post_init():
    "test post-initializer."
    assert Code('x=3 +y').text == "x = 3 + y\n"


def test_func_helper1():
    "test codegen helpers."
    context = CodeGenContext()
    helper = CodeBuilder(context)
    assert helper.context.func_suffix == 0
    assert helper.context.var_suffix == 0
    assert helper.v() == "w0"
    assert helper.f() == "f0"
    assert helper.v(name="x") == "x1"
    assert helper.f(name="g") == "g1"


def test_func_helper2():
    "test codegen helpers."
    helper = CodeBuilder(CodeGenContext())
    helper.header()
    assert helper.header_ == "def f0(w0):\n"


def test_func_helper3():
    "test codegen helpers."
    helper = CodeBuilder(CodeGenContext())
    helper.header(num_args=0)
    assert helper.header_ == "def f0():\n"


def test_func_helper4():
    "test codegen helpers."
    helper = CodeBuilder(CodeGenContext())
    helper.header(num_args=2)
    assert helper.header_ == "def f0(w0, w1):\n"


def test_func_helper5():
    "test codegen helpers."
    helper = CodeBuilder(CodeGenContext())
    helper.header(vname="x")
    assert helper.header_ == "def f0(x0):\n"


def test_func_helper6():
    "test codegen helpers."
    helper = CodeBuilder(CodeGenContext())
    helper.header(fname="g")
    assert helper.header_ == "def g0(w0):\n"


def test_func_helper7():
    "test codegen helpers."
    helper = CodeBuilder(CodeGenContext())
    helper.header(params=['x', 'y', 'z'])
    assert helper.header_ == "def f0(x, y, z):\n"
