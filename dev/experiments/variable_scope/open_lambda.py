"lambdadef with undeined free variable."
from pprint import pprint

# contains a free variable 'z', which is not undefined in globals().
f = lambda x, y: x + y + z

# function def version of the above.


def g(x, y):
    return x + y + z


assert f.__globals__ is globals()
# pprint(f.__code__.co_freevars)  # None
# pprint(f.__code__.co_names)  # 'y'
# pprint(f.__code__.co_varnames)  # 'x'
assert f.__code__.co_freevars == ()
assert f.__code__.co_names == ('z',)
assert f.__code__.co_varnames == ('x', 'y')

assert g.__globals__ is globals()
# pprint(g.__code__.co_freevars)  # None
# pprint(g.__code__.co_names)  # 'y'
# pprint(g.__code__.co_varnames)  # 'x'
assert g.__code__.co_freevars == ()
assert g.__code__.co_names == ('z',)
assert g.__code__.co_varnames == ('x', 'y')

try:
    f(3, 6)
except NameError as e:
    pprint(e)

z = 4
print(f(3, 6))
print(g(3, 6))
