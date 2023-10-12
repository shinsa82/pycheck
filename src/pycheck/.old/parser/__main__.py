"""
convenient tool to parse typespecs.
'python -m pycheck.parser' to run.
"""
from argparse import ArgumentParser, FileType, Namespace

from lark import Tree

from . import parse_typespec

ap: ArgumentParser = ArgumentParser(
    prog=f'python -m {__package__}',
    description='Parse a typespec (like "int -> int") given in a file.'
)
ap.add_argument(
    'in_file',
    help='input file that contains a typespec. if "-" is specified, it reads from standard input.',
    type=FileType(mode='r', encoding='utf-8')
)
ns: Namespace = ap.parse_args()

print(f'input file = {ns.in_file.name}')
typespec = ns.in_file.read().strip()
print('\ntypespec to be parsed =')
print('-' * 10)
print(typespec)
print('-' * 10)
print('\nparsing...')
t: Tree = parse_typespec(typespec)
print('parsed tree = ')
print('-' * 10)
print(t)
print('-' * 10)
print('\npretty printed =')
print('-' * 10)
print(t.pretty())
print('-' * 10)
