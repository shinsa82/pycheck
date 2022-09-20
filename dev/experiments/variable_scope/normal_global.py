from pprint import pprint

y = 3
pprint(globals())  # current global scope.
f = eval('lambda x: x+y')  # <- evaled with default global scope.

pprint(f.__globals__)  # <- "global scope" that f will use.
pprint(globals())  # updated global scope.

assert f.__closure__ is None
assert f.__globals__ is globals()
print(f(3))
