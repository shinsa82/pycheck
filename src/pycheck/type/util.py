"Utilities for types."
from textwrap import indent

from . import Base, FunctionType, Generic, RefinementType, Sum


def pretty(typ) -> str:
    "pretty print a Type object."
    if isinstance(typ, FunctionType):
        ret = typ.__class__.__name__
        children = indent("\n".join(
            [f"{v}:\n{indent(pretty(t),'  ')}" for v, t in typ.args.args_type.items()]), '  ')
        ret += ("\n" + children)
        ret += f"\n  ->\n" + indent(pretty(typ.return_type), '    ')
        return ret
    elif isinstance(typ, RefinementType):
        bv = typ.base_var if len(typ.base_var) > 0 else '(empty)'
        ret = f"{typ.__class__.__name__}\n" + indent(
            f"{bv}\n{pretty(typ.base_type)}\n{typ.predicate}\nsignature: {typ.signature}", '  ')
        return ret
    elif isinstance(typ, Sum):
        children = indent("\n".join([pretty(t) for t in typ.choices]), '  ')
        return typ.__class__.__name__ + "\n" + children
    elif isinstance(typ, (Base, Generic)):
        return typ.text
    else:
        raise NotImplementedError
