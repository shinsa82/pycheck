"Code generation helper."
from dataclasses import dataclass
from textwrap import indent

from autopep8 import fix_code
from lark import Tree

from ..parsing import reconstruct
from .const import Code, CodeGenContext


@dataclass
class FuncHelper:
    "helper to generate function code."
    context: CodeGenContext
    header_: str = None
    entry_point: str = None
    comment_: str = None
    body_: str = None

    def __post_init__(self):
        pass

    def f(self, name="f"):
        "generate new function name."
        return f"{name}{self.context.get_fsuf()}"

    def v(self, name="w"):
        "generate new variable name."
        return f"{name}{self.context.get_vsuf()}"

    def header(self, params=None, num_args=1, vname="w", fname="f"):
        """
        generate function header.

        if params is specified, num_args and vname are ignored.
        """
        if params is None:
            params = []
            for _ in range(num_args):
                params.append(self.v(name=vname))
        self.entry_point = self.f(name=fname)
        self.header_ = fix_code(
            f"def {self.entry_point}({','.join(params)}):\n")

    def comment(self, msg: str):
        "generate a general comment line."
        self.comment_ = f"# {msg}\n"

    def comment_gen(self, type_: Tree):
        "generate a comment line (gen)."
        self.comment_ = f"# gen a value of '{reconstruct(type_)}'\n"

    def comment_tc(self, type_: Tree):
        "generate a comment line (typecheck)."
        return f"# type check against '{reconstruct(type_)}'\n"

    def body(self, text):
        "set body text."
        self.body_ = fix_code(text)

    def _gen_func(self) -> str:
        "create a function definition."
        return fix_code(self.header_ + indent(
            (self.comment_ or "") +
            (self.body_ or "pass"),
            ' ' * 2)
        )

    def code(self) -> Code:
        "return generated code."
        return Code(self._gen_func(), entry_point=self.entry_point)
