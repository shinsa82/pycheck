"NumPy random generators used in typechecking codes."
from numpy.random import Generator, default_rng

rng: Generator = default_rng()


def rand_int() -> int:
    "return a random integer."
    return rng.integers(-100, 100, endpoint=True)


def rand_bool() -> bool:
    "return a random boolean."
    return rng.choice([False, True])
