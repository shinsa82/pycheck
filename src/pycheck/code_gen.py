"Code generator from reftype spec."
from dataclasses import dataclass
from logging import getLogger
from typing import Any

from .reftype import RefType

logger = getLogger(__name__)


@dataclass
class Code:
    "Code to be executed by typechecker."
    pass


def code_gen(value: Any, reftype: RefType) -> Code:
    """
    generate a code from reftype.

    codes are valid Python programs,
    assuming that random generator rand_<T> is provided.
    """
    logger.info("generating code from reftype %s...", reftype.type)
    return Code()
