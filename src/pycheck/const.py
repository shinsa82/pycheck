"""
Constants and type aliases used in PyCheck.
"""
from typing import TypeAlias

# common prefix of PyCheck constants
PYCHECK_PREFIX = "pycheck"
# used to store a reftype to a function.
REFTYPE = f"__{PYCHECK_PREFIX}_reftype__"

TypeStr: TypeAlias = str  # a string that denotes a (refinement) type


class PyCheckAssumeError(Exception):
    "denotes an assumption error."

    def __init__(self, msg):
        super().__init__(msg)


class PyCheckAssertError(Exception):
    "denotes an assertion error."

    def __init__(self, step, msg):
        super().__init__(msg)
        self.step = step


class PyCheckFailError(Exception):
    "denotes a execution fail in a generated function."

    def __init__(self):
        super().__init__("Execution (intendedly) failed in a generated function")
