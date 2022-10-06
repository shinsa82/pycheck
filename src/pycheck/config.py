"configuration of PyCheck."
from dataclasses import dataclass


@dataclass
class Config:
    max_iter: int = 100
