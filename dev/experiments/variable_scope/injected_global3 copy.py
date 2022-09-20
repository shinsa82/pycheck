from pprint import pprint

pprint(globals())  # current global scope.
l = {}
# v-- lambda exp has a free variable. evaled with default global scope.
f = eval('lambda x: x+y', globals(), l)  # <- with injected global
# <- success without failure

pprint(f.__globals__)  # <- "global scope" that f will use.
assert '__builtins__' in f.__globals__
assert f.__globals__ is globals()
pprint(globals())  # updated global scope.
assert f.__closure__ is None  # <- note that the closure is None.

pprint(f.__code__.co_freevars)  # None
pprint(f.__code__.co_names)  # 'y'
pprint(f.__code__.co_varnames)  # 'x'

try:
    print(f(3))
except NameError as e:
    pprint(e)

try:
    y = 2
    assert 'y' in globals()
    print(f(3))
except NameError as e:
    pprint(e)

g['y'] = 3
assert 'y' in f.__globals__
print(f(3))
