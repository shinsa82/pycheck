"test utilities."
from rich import print  # pylint: disable=redefined-builtin
from rich.markdown import Markdown
from rich.markup import escape
from sympy import Dummy, Lambda, S, srepr

from pycheck import Config, PyCheckAssumeError, RefType, TypeStr, code_gen
from pycheck.executor import evaluate, execute
from pycheck.random import rand_int
from pycheck.codegen.sympy_lib import List

# pylint:disable=invalid-name


def true_func():
    "get new True constant function, 'lambda x: true', with a fresh variable."
    return Lambda((Dummy('x'),), S.true)


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

    if isinstance(val, list):
        val = List(*val)

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


def codegen_gen_and_exec(typ: TypeStr, constraint=None, custom_env=None, custom_tc=None, max_iter=20, func=False, strict=False):
    """
    (2023/06 latest) Subroutine for test that generates a generator code for the given type
    and execute it.
    If func is True, generation will be done once and argument are generated iteratively instead. 
    If custom_tc is a callable, this will be used to type check generated values.
    """
    print(f"type = {escape(typ)}")
    reftype = RefType(typ, strict=False)
    if constraint is None:
        constraint = true_func()
    print(f"constraint = {constraint}")

    code = code_gen(reftype=reftype, mode="gen", constraint=constraint)
    print("code:")
    print(code)

    if custom_tc:
        check_code = custom_tc
    else:
        check_code = code_gen(reftype=reftype, is_delta=False)

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
        if custom_env:
            constraint = constraint.subs(custom_env)
            print(f"substituted constraint = {constraint}")

        # execute generation by the specified times
        while True:
            try:
                if custom_env:
                    res = code(custom_env)()
                    check_code = check_code.subs(custom_env)
                else:
                    res = code()()  # generate one value

                if isinstance(res, list):
                    res = List(*res)

                # typecheck generated value
                is_typed = check_code(res) and constraint(res)
                # is_typed = constraint(res) # workaround
                if is_typed:
                    print(f"{res}  -  [green](maybe) well-typed.[/]")
                else:
                    print(f"{res}  -  [red](must be) ill-typed.[/]")
                assert is_typed

                iter += 1
                if iter == max_iter:
                    return
            except PyCheckAssumeError:
                print("[yellow]Assume failed[yellow]")
