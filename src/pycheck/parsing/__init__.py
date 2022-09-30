"""
Parser of reftype.

Grammar files are:
- reftype.lark by @shinsa82.
- python3.lark, from Lark bundled example, by Erez Shinan.
"""
from .gen_parser import parser
from .parse_impl import parse_reftype
