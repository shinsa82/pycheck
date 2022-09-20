"""
Types for expressing (dependent and) refinement types in mypy.

These wrapper classes can be used to express PyCheck types in scope of mypy.
In other words, programs that use these classes can be safely typechecked by mypy.  
See https://github.ibm.com/SHINSA/pycheck/issues/6 for more description.
See test/type/test_mypy.py for unit tests.
"""
from typing import Any, Callable


class RefType:
    """
    Expresses refinemet types with use of Annotated as follows:
    { x:T | p(x, ...) } := Annotated[T, RefType('x', p)].
    """

    def __init__(self, var: str, predicate: Callable[..., bool]):
        self.var = var
        self.predicate = predicate


class CallRefType:
    """
    Expresses refinemet types with Callable.
    f is defined by def f(x, y, ...): ... and f is of type Callable[[T1, ..., Tn], T], then
    f is of type Annotated[Callable[...], CallRefType(params=['x', 'y', ...])].
    """

    def __init__(self, params):
        self.params = params
        ...
