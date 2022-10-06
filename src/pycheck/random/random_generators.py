"NumPy random generators used in typechecking codes."
from numpy.random import Generator, default_rng

rng: Generator = default_rng()


def rand_int() -> int:
    "return a random integer."
    return rng.integers(-1_000, 1_000, endpoint=True)
