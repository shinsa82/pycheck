from pprint import pprint

pprint(globals())  # current global scope.
# <- lambda exp has a free variable. evaled with default global scope.
f = eval('lambda x: x+y')
# <- success without failure

pprint(f.__globals__)  # <- "global scope" that f will use.
pprint(globals())  # updated global scope.

assert f.__closure__ is None  # <- note that the closure is None.
assert f.__globals__ is globals()
print(f(3))
