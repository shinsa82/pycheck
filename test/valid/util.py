from typing import Callable, Union

from pandas import DataFrame
from pycheck.parser import parse
from pycheck.spec import TypeSpec, typespec
from pycheck.type import Type
from pycheck.type.util import pretty
from pycheck.util import get_logger

debug, info, _, _, _ = get_logger(__name__)


def p(typ: str):
    "test utility."
    return parse(typ, globals_=locals())


def dump(opcodes):
    info('')
    info('----------------')
    info(f'-- opcodes ({len(opcodes)}) --')
    for code in opcodes:
        info(code)

    print('')
    print(f'-- opcodes ({len(opcodes)}) --')
    for i, code in enumerate(opcodes):
        print(f"{i}: {code}")


def run(tc, f: Callable = None, t: Union[str, Type] = None):
    """
    Generates opcodes for typespec assigned to a function 'f',
    and returns the opcodes.
    """
    if t is None:
        spec: TypeSpec = typespec(f, raw=True)
        text = spec.text
        typ = spec.ast
    elif isinstance(t, str):
        text = t
        typ = parse(t, globals_=globals() | locals())
    else:  # t is Type
        text = t.text
        typ = t
    print('')
    print('-- typespec --')
    print(text)
    print('')
    print('-- pretty --')
    print(pretty(typ))
    codes = tc.typecheck0(f, t=typ)
    dump(codes)
    return codes


def show_stat(detail) -> None:
    "shows stat detail."
    print()
    df = DataFrame.from_records(detail)
    df['length'] = df['value'].map(len)
    print(df)

    df_true = df.query("satisfied == True")
    df_false = df.query("satisfied == False")
    print(df_true)
    print()
    print(df_true.describe())
    print()
    print(df_false)
    print()
    print(df_false.describe())
