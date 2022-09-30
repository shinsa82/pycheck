"Class for refinement type spec."
from dataclasses import dataclass, field
from logging import getLogger

from lark import Tree

from .const import TypeStr
from .parsing import parse_reftype

logger = getLogger(__name__)


@dataclass
class RefType:
    "type spec dataclass."
    type: TypeStr
    ast: Tree = field(init=False)

    def __post_init__(self):
        logger.info("parsing reftype '%s'", self.type)
        self.ast = parse_reftype(self.type)
        logger.info("parsed.")
