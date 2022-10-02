"Executor of generated codes."
from logging import getLogger
from typing import Any, Callable

from .result import Result

logger = getLogger(__name__)


def execute(tc_func: Callable, term: Any) -> Result:
    "iteratively execute the code and returns its result."
    logger.info("executing typechecking code...")
    logger.info("typechecking funciton = %s", tc_func)
    logger.info("term = %s", term)
    # logger.info("copying environments")
    # for k, v in locals_.items():
    #     globals()[k] = v
    logger.info("starting execution.")
    b = tc_func(term)
    logger.info("executed. result = %s", b)
    return Result(well_typed=b)
