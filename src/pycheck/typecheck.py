"Main typechecking routines."
from logging import getLogger
from typing import Any

from .codegen import Code, code_gen
from .const import TypeStr
from .executor import execute, PyCheckAssumeError, PyCheckFailError
from .random.random_generators import rand_int, rand_bool
from .reftype import RefType
from .result import Result
from .type_annotation import get_reftype

logger = getLogger(__name__)


def typecheck(term: Any, reftype_str: TypeStr = None, detail=False) -> bool | Result:
    "typecheck the term against the reftype and returns its result."
    logger.info("typechecking %s: %s", term, reftype_str)
    if reftype_str:
        reftype = RefType(reftype_str)
    else:
        # TODO: term should be callable?
        reftype = get_reftype(term)

    code: Code = code_gen(term, reftype)
    # code.add_line(f"tc_func = {code.entry_point}")
    locals_ = {'rand_int': rand_int, 'rand_bool': rand_bool,
               'PyCheckAssumeError': PyCheckAssumeError,
               'PyCheckFailError': PyCheckFailError}
    # want to avoid use of 'exec()', but I'm using it as it is simple...
    exec(code.text, globals(), locals_)  # typechecking function
    logger.info("defined sub- and main functions:")
    logger.info(locals_)
    logger.info("entrypoint:")
    logger.info(locals_[code.entry_point])

    result: Result = execute(locals_[code.entry_point], term)
    logger.info(result)

    return result if detail else result.well_typed
