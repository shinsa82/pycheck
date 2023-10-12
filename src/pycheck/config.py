"configuration of PyCheck."
from dataclasses import dataclass


@dataclass
class Config:
    max_iter: int = 100

    def max_iteration(self, n: int) -> "Config":
        self.max_iter = n
        return self


def config():
    return Config()
