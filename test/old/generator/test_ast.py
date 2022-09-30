"""
Test for ast built-in module.
"""
import ast


def test_parse_eval():
    "play with built-in ast.parse()"
    node = ast.parse('x>0', filename='<string>',
                     mode="eval", type_comments=True)
    print(node)
    print("-- parse tree --")
    print(ast.dump(node, indent=2))
    print("-- parse tree w/o field annotations --")
    print(ast.dump(node, annotate_fields=False, indent=2))
    print("-- parse tree w/ attributes --")
    print(ast.dump(node, include_attributes=True, indent=2))
