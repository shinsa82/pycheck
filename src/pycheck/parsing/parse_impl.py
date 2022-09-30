"Utilities for parsing reftype and others."
from logging import getLogger

from lark import Tree

from ..const import TypeStr
from .gen_parser import parser

logger = getLogger(__name__)


def parse_reftype(reftype: TypeStr) -> Tree:
    """parse given typespec string and return constructed Tree."""
    return parser.parse(reftype)
