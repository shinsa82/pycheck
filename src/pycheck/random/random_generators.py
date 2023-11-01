"NumPy random generators used in typechecking codes."
from logging import getLogger

from numpy.random import Generator, default_rng


class Random:
    def __init__(self):
        self.rng = default_rng()

    def set_seed(self, seed):
        logger.info("set seed to %s", seed)
        self.rng = default_rng(seed)


logger = getLogger(__name__)
# rng: Generator = default_rng()
my_random = Random()

# default lower/upper bounds
INT_LOWER_BOUND = -100
INT_UPPER_BOUND = 100


def rand_int(min_=INT_LOWER_BOUND, max_=INT_UPPER_BOUND) -> int:
    """
    return a random integer between the bound.
    """
    if min_ is None and max_ is None:
        min_ = INT_LOWER_BOUND
        max_ = INT_UPPER_BOUND
    elif min_ is None:
        min_ = min(INT_LOWER_BOUND, max_ - 100)
    elif max_ is None:
        max_ = max(INT_UPPER_BOUND, min_ + 100)

    return int(my_random.rng.integers(min_, max_, endpoint=True))


def rand_bool(p=0.5) -> bool:
    """
    return a random boolean.
    optional p is a prob. of True.
    """
    return bool(my_random.rng.choice([False, True], p=[1.0 - p, p]))


def set_seed(seed):
    my_random.set_seed(seed)
