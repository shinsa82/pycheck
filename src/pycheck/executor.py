"Executor of generated codes."
from .code_gen import Code
from .result import Result


def execute(code: Code) -> Result:
    "iteratively execute the code and returns its result."
    return Result()
