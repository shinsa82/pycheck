"Implements symbolic computation."
from dataclasses import dataclass
from logging import getLogger
from typing import Any

from lark.visitors import Transformer

from ..parsing import parse_expression

logger = getLogger(__name__)


@dataclass
class Var:
    "symbolic variable."
    name: str


@dataclass
class Exp:
    "symbolic expression."
    term: Any

    def __and__(self, other):
        logger.debug("__and__ called")
        return self

    def __add__(self, other):
        if isinstance(other, Exp):
            self.term = ['+', self.term, other.term]  # symbolic + symbolic
            return self
        else:
            self.term = ['+', self.term, other]  # symbolic + value
            return self

    def __radd__(self, left):
        if isinstance(left, Exp):
            self.term = ['+', left.term, self.term]   # symbolic + symbolic
            return self
        else:
            self.term = ['+', left, self.term]  # symbolic + value
            return self

    def __gt__(self, other):
        logger.debug("__gt__ called")
        ret = Exp(('>', (self, other)))
        return ret

    def __ge__(self, other):
        ret = Exp(('>=', (self, other)))
        return ret

    def __call__(self, var: str):
        pass


def reduction(exp: Any):
    "parse expression and perform symbolic reduction."
    logger.debug("parsing '%s'", exp)
    ast = parse_expression(exp)
    logger.debug("\n%s", ast.pretty())

    if ast.data == "python3__funccall":
        assert ast.children[0].data == "python3__lambdef"
        assert ast.children[1].data == "python3__arguments"
        assert len(ast.children[1].children) == 1
    else:
        logger.warning("reduction of rule '%s' is not supported yet", ast.data)
    raise NotImplementedError("reduction is not implemented yet.")


def eval_refinement(refinement: str, var: str) -> Exp:
    res: Exp = eval(refinement, globals(), {var: Exp(Var(var))})
    logger.debug(res)
    return
