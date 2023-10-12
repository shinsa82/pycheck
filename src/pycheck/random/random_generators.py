"NumPy random generators used in typechecking codes."
from numpy.random import Generator, default_rng

rng: Generator = default_rng()

INT_LOWER_BOUND = -100
INT_UPPER_BOUND = 100


def rand_int(min_=INT_LOWER_BOUND, max_=INT_UPPER_BOUND) -> int:
    "return a random integer."
    if min_ is None and max_ is None:
        min_ = INT_LOWER_BOUND
        max_ = INT_UPPER_BOUND
    elif min_ is None:
        min_ = min(INT_LOWER_BOUND, max_ - 100)
    elif max_ is None:
        max_ = max(INT_UPPER_BOUND, min_ + 100)

    return int(rng.integers(min_, max_, endpoint=True))


def rand_bool(p=0.5) -> bool:
    """
    return a random boolean.
    optional p is a prob. of True.
    """
    return bool(rng.choice([False, True], p=[1.0 - p, p]))
