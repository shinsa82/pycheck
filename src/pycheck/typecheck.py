"Main typechecking routines."
from typing import Any

from .code_gen import Code, code_gen
from .const import TypeStr
from .reftype import RefType
from .result import Result
from .type_annotation import get_reftype
from .executor import execute


def typecheck(term: Any, reftype_str: TypeStr = None, detail=False) -> bool | Result:
    "typecheck the term against the reftype and returns its result."
    if reftype_str:
        reftype = RefType(reftype_str)
    else:
        # TODO: term should be callable?
        reftype = get_reftype(term)

    code: Code = code_gen(term, reftype)
    result: Result = execute(code)

    return result if detail else result.well_typed
