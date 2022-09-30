"""
Pycheck: refinement-type based type checker using PBRT.
"""
from importlib.metadata import version as _version

from .result import Result
from .type_annotation import get_reftype, has_reftype, reftype
from .typecheck import typecheck

__version__ = _version(__name__)
