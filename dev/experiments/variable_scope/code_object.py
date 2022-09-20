"""
introduction of code object.
"""
from inspect import getclosurevars
from pprint import pprint

v = 1


def definer():
    print('-- definer --')
    z = 5
    pprint(locals())
    # contains a free variable 'z', which is defined in enclosing local scope.
    # contains a free variable 'w', which is not undefined in any scope.
    # evaluated with default global and local scopes.

    def g(x, y):
        pprint(locals())
        o = v + w + x + y + z
        pprint(locals())
        return o

    print('----')
    return g


f = definer()

print('+' * 10)
assert f.__globals__ is globals()  # glocal scope is the same.
pprint(f.__closure__)
pprint(f.__code__.co_freevars)
pprint(f.__code__.co_names)
pprint(f.__code__.co_varnames)
assert f.__code__.co_freevars == ('z',)
# assert f.__code__.co_names == ('v', 'w')
assert f.__code__.co_varnames == ('x', 'y', 'o')

# other attrbutes
print('-' * 10)
print(f"{f.__code__.co_argcount=}")
print(f"{f.__code__.co_code=}")
print(f"{f.__code__.co_cellvars=}")
print(f"{f.__code__.co_consts=}")
print(f"{f.__code__.co_filename=}")
print(f"{f.__code__.co_firstlineno=}")
print(f"{f.__code__.co_flags=}")
print(f"{f.__code__.co_lnotab=}")
print(f"{f.__code__.co_posonlyargcount=}")
print(f"{f.__code__.co_kwonlyargcount=}")
print(f"{f.__code__.co_name=}")
print(f"{f.__code__.co_nlocals=}")
print(f"{f.__code__.co_stacksize=}")
print('+' * 10)

print(getclosurevars(f))

print('invoking f...')
try:
    f(3, 6)
except NameError as e:
    pprint(e)

w = 5
print(f(3, 6))
