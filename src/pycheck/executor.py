"Executor of generated codes."
from logging import getLogger
from typing import Any, Callable

from sympy import S

from .codegen import Code
from .config import Config
from .const import PyCheckAssertError, PyCheckAssumeError, PyCheckFailError
from .random.random_generators import rand_bool, rand_int
from .result import Result

logger = getLogger(__name__)


def execute(tc_func: Callable, term: Any, config: Config = None) -> Result:
    "iteratively execute the code and returns its result."
    if config is None:
        config = Config()
    logger.info("executing typechecking code...")
    logger.info("typechecking funciton = %s", tc_func)
    logger.info("term = %s", term)
    # logger.info("copying environments")
    # for k, v in locals_.items():
    #     globals()[k] = v
    try:
        logger.info("starting execution. max_iter = %s", config.max_iter)
        success = 0
        fail_assume = 0
        while success < config.max_iter:
            try:
                b = tc_func(term)
                if not b:
                    raise PyCheckAssertError(step=success+1, msg="dummy")
                success += 1
            except PyCheckAssumeError as err:
                logger.debug(err)
                fail_assume += 1
        logger.info("successfully completed full iteration. result = %s", b)
        return Result(well_typed=b, max_iter=config.max_iter, retry=fail_assume)
    except PyCheckAssertError as err:
        # when type-checking failed
        logger.warning("execution failed at iteration #%s", err.step)
        return Result(well_typed=False, failed_at=err.step, max_iter=config.max_iter)
