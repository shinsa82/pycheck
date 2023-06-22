"test utilities."
from rich import print  # pylint: disable=redefined-builtin
from rich.markdown import Markdown
from rich.markup import escape
from sympy import Dummy, Lambda, S, srepr

from pycheck import Config, PyCheckAssumeError, RefType, TypeStr, code_gen
from pycheck.executor import evaluate, execute
from pycheck.random import rand_int

# pylint:disable=invalid-name


def true_func():
    "get new True constant function, 'lambda x: true', with a fresh variable."
    return Lambda((Dummy('x'),), S.true)


# def exec_code(code, val, is_typed):
#     "subroutine for test."
#     # locals_ = {}

#     # render code block using rich Markdown
#     md = Markdown("```python\n" + code.text + "```")
#     print("code:")
#     print(md)

#     f = evaluate(code)
#     # execute typechecking only once
#     res = execute(f, term=val, config=Config(max_iter=1))
#     print(res)

#     assert res.well_typed == is_typed


def codegen_tc_and_exec(typ: TypeStr, val, is_typed: bool = True, max_iter=1):
    """
    (2023/06 latest) Subroutine for test that generates a typechecking code for the given type
    and execute it.
    """
    print(f"type = {escape(typ)}")
    reftype = RefType(typ)
    print(f"value = {val}")
    code = code_gen(reftype=reftype)
    print("code:")
    print(code)

    print(f"\niterating {max_iter} times:")

    try:
        for _ in range(max_iter):
            # execute typechecking the specified times
            res = code(val)
            print(res)
            assert res
    except AssertionError as e:
        print("[red](must be) ill-typed.[/]")
        assert not is_typed
    else:
        print("[green](maybe) well-typed.[/]")
        assert is_typed


def codegen_gen_and_exec(typ: TypeStr, constraint=None, max_iter=10, func=False):
    """
    (2023/06 latest) Subroutine for test that generates a generator code for the given type
    and execute it.
    If func is True, generation will be done once and argument are generated iteratively instead. 
    """
    print(f"type = {escape(typ)}")
    reftype = RefType(typ)
    if constraint is None:
        constraint = true_func()
    print(f"constraint = {constraint}")

    code = code_gen(reftype=reftype, mode="gen", constraint=constraint)
    print("code:")
    print(code)

    if func:
        f = code()
        print(f"function generated = {f}")

        print(f"\niterating {max_iter} times:")
        for _ in range(max_iter):
            arg = rand_int()
            res = f(arg)  # TODO: respect arg type
            print(f"{arg} -> {res}")
    else:
        print(f"\ngenerating {max_iter} times:")

        iter = 0
        # execute generation by the specified times
        while True:
            try:
                res = code()
                print(res)
                iter += 1
                if iter == max_iter:
                    return
            except PyCheckAssumeError:
                print("[yellow]Assume failed[yellow]")


# def exec_code_new(code, val, is_typed, max_iter=1):
#     "subroutine for test, for new code generator."

#     # render code block using rich Markdown
#     print("code:")
#     print(code)
#     # print("code (srepr):")
#     # print(srepr(code))

#     for _ in range(max_iter):
#         # execute typechecking once
#         res = code(val)
#         print(res)
#         assert res == is_typed


# def exec_gen_code(code, max_iter=10):
#     "subroutine for test, for new code generator."

#     # render code block using rich Markdown
#     print("code:")
#     print(code)
#     # print("code (srepr):")
#     # print(srepr(code))

#     # execute typechecking only once
#     for _ in range(max_iter):
#         res = code()
#         print(res)
