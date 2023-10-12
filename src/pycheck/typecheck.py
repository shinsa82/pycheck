"Main typechecking routines."
from logging import getLogger
from typing import Any

from .codegen import Code, code_gen
from .config import config as config_
from .const import TypeStr
from .executor import execute
from .reftype import RefType
from .result import Result
from .type_annotation import get_reftype
from time import perf_counter
from .util import perf_ms
logger = getLogger(__name__)


def typecheck(term: Any, reftype_str: TypeStr = None, detail=False, config=None) -> bool | Result:
    "main entry point of PyCheck: typecheck the term against the reftype and returns its result."
    s0 = perf_counter()
    s1 = perf_counter()
    if reftype_str:
        reftype = RefType(reftype_str)
    else:
        # TODO: need to check if the term is callable or not?
        reftype = get_reftype(term)
    logger.info("typechecking %s against '%s'", term, reftype.type)
    e1 = perf_counter()
    logger.info("parsing in %s", perf_ms(s1, e1))

    s2 = perf_counter()
    code: Code = code_gen(reftype)
    e2 = perf_counter()
    logger.info("code generation in %s", perf_ms(s2, e2))

    config = config or config_()
    s3 = perf_counter()
    result: Result = execute(code, term, config)
    e3 = perf_counter()
    logger.info(result)
    logger.info("execution in %s, in avg %s", perf_ms(s3, e3),
                perf_ms(s3, e3, divide=result.max_iter + result.retry))
    e0 = perf_counter()

    logger.info("type checking finished in %s", perf_ms(s0, e0))
    return result if detail else result.well_typed
