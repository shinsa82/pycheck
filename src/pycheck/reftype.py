"Class for refinement type spec."
from dataclasses import dataclass, field
from logging import getLogger

from lark import Tree

from .const import TypeStr
from .parsing import parse_reftype
from .types.const import PycheckType, get_type

logger = getLogger(__name__)


@dataclass
class RefType:
    "type spec dataclass."
    type: TypeStr  # original type string
    strict: bool = True
    ast: Tree = field(init=False)  # Lark parse tree of `type`
    type_obj: PycheckType = field(init=False)

    def __post_init__(self):
        logger.info("parsing reftype '%s'", self.type)
        self.ast = parse_reftype(self.type)
        self.type_obj = get_type(
            self.ast, free_variables=[], strict=self.strict)
        logger.info("parsed.")
