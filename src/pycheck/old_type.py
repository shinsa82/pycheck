"""
PyCheck-specific types for expressing (dependent and) refinement types.
"""


class Refinement:
    """
    Refinement types.

    TODO: Definition of Refinement class in core.py should be merged to this.
    """

    def __init__(self, base: type, var: str, predicate) -> None:
        "base: base type, var: variable name, predicate: predicate function"
        self.base = base
        self.var = var
        self.predicate = predicate

    def __str__(self) -> str:
        pass


class Function:
    """
    Function types.
    """

    def __init__(self, args, returns):
        self.arg_types = args
        self.return_type = returns
