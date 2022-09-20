from inspect import currentframe, getframeinfo, stack
from pprint import pprint


def f(y, s):
    stacks = stack(context=3)
    # pprint(stacks)
    for i, fi in enumerate(stacks, start=1):
        print()
        print(f'*** {i} ***')
        pprint(fi)

        pprint(fi.frame)
        pprint(fi.filename)
        pprint(fi.lineno)
        pprint(fi.function)
        for i, li in enumerate(fi.code_context):
            print(('> ' if i == fi.index else '  ') + li, end='')
        pprint(fi.index)

        f = fi.frame
        print('-- globals --')
        pprint(f.f_globals)
        print('-- locals --')
        pprint(f.f_locals)

def g(x):
    y = 'test'
    f(x, y)


if __name__ == '__main__':
    from pandas import DataFrame
    z = 3
    g(z)
