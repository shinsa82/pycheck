"""shows function signatures."""
from inspect import Signature, signature
from pprint import pprint
from traceback import print_exc
from typing import Any, get_type_hints


def add(y: float, x: int) -> float:
    return x + 1


print('locals():')
pprint(locals())

print()
print('globals():')
pprint(globals())

# typing.get_type_hints returns a dict of ('var name', 'type').
# return type is presented as value for a key 'return' (it works since 'return' is a reserved word)
# note that order of arguments is not preserved since it's a dict.
print()
# reveal_type(get_type_hints(add)) # builtins.dict[builtins.str, Any]
type_hints: dict[str, Any] = get_type_hints(add)
pprint(type_hints)


print()
# inspect.signature returns a Signature object.
# .parameters returns an object of a kind of OrderedDict.
# return type can be obtained by .return_annotation property.
# Thus argument order seems to be preserved.

# reveal_type(signature(add)) # inspect.Signature
sig: Signature = signature(add)
pprint(sig)
pprint(sig.parameters)
pprint(sig.return_annotation)

# As expected, signature of a lambda function would be without type annotation.
print()
l = lambda x, y: x + y
sig_l: Signature = signature(l)
print(sig_l)
# reveal_type(sig_l.parameters)  # typing.Mapping[builtins.str, inspect.Parameter
pprint(sig_l.parameters)
pprint(sig_l.return_annotation)

print()
assert callable(map)  # map is callable, but...
try:
    # cannot get signature of map, since it's a constructor, not function.
    sig_map: Signature = signature(map)
except ValueError as e:
    print(f'ValueError raised.')
    # print_exc(e)

# reveal_type(map)
print(signature(map.__init__)) # can be obtained, but not useful
print(signature(map.__call__)) # can be obtained, but not useful
