"""
lambdadef with undeined free variable.

what if a lambda expression is inside a local scope?
"""
from pprint import pprint


def definer():
    z = 5
    # contains a free variable 'z', which is defined in local scope.
    # contains a free variable 'w', which is not undefined in any scope.
    # evaluated with default global and local scopes.
    return lambda x, y: w + x + y + z


f = definer()

assert f.__globals__ is globals()  # glocal scope is the same.
pprint(f.__code__.co_freevars)  # None
pprint(f.__code__.co_names)  # 'y'
pprint(f.__code__.co_varnames)  # 'x'
assert f.__code__.co_freevars == ('z',)
assert f.__code__.co_names == ('w',)
assert f.__code__.co_varnames == ('x', 'y')

try:
    f(3, 6)
except NameError as e:
    pprint(e)

z = 4
print(f(3, 6))
