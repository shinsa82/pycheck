"Reconstruction of parse tree for printing debug information."
from lark import Tree
from lark.reconstruct import Reconstructor

from .gen_parser import parser


def reconstruct(ast: Tree) -> str:
    return Reconstructor(parser).reconstruct(ast)
