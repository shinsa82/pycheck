"NumPy random generators used in typechecking codes."
from numpy.random import Generator, default_rng

rng: Generator = default_rng()

INT_LOWER_BOUND = -100
INT_UPPER_BOUND = 100


def rand_int(min_=INT_LOWER_BOUND, max_=INT_UPPER_BOUND) -> int:
    "return a random integer."
    return rng.integers(min_, max_, endpoint=True)


def rand_bool() -> bool:
    "return a random boolean."
    return rng.choice([False, True])
