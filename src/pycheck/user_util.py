"utilities used by user of PyCheck."
from logging import DEBUG, INFO, WARNING, basicConfig

from rich.logging import RichHandler
from sympy import S

from .codegen import code_gen
from .const import TypeStr
from .reftype import RefType


def verbose(level: int | str = 0):
    """
    set global logging level.

    0, 1, 2 sets log level WARNING, INFO, DEBUG, respectively.
    """
    match level:
        case 0:
            level_set = ('WARNING', WARNING)
        case str(level) if level.lower() in ['warning', 'warn']:
            level_set = ('WARNING', WARNING)
        case 1:
            level_set = ('INFO', INFO)
        case str(level) if level.lower() in ['info']:
            level_set = ('INFO', INFO)
        case 2:
            level_set = ('DEBUG', DEBUG)
        case str(level) if level.lower() in ['debug']:
            level_set = ('DEBUG', DEBUG)
        case _:
            raise ValueError(f"illegal verbose level: {level}")

    FORMAT = "%(message)s"
    basicConfig(level=level_set[1], format=FORMAT, datefmt="[%X]", handlers=[
                RichHandler()], force=True)
    print(f"verbose level set to {level_set[0]}")


def parse(t: TypeStr) -> RefType:
    "parsing utility."
    return RefType(t)


def generator(t: TypeStr, constraint=None):
    "get the data generator for the type."
    if constraint is None:
        return code_gen(reftype=RefType(t), mode="gen")()
    else:
        return code_gen(reftype=RefType(t), mode="gen", constraint=S(constraint))()
