"Code generation helper."
from dataclasses import dataclass
from logging import getLogger
from textwrap import indent

from autopep8 import fix_code
from lark import Tree
from rich.markdown import Markdown

from ..parsing import reconstruct
from .const import Code, CodeGenContext, CodeGenResult

logger = getLogger(__name__)


@dataclass
class CodeBuilder:
    "code builder to generate function deinition code."
    context: CodeGenContext
    header_: str = None
    params_: list[str] = None
    entry_point: str = None
    comment_: str = None
    body_: str = ""

    def __post_init__(self):
        pass

    def f(self, name="f"):
        "generate new function name."
        return f"{name}{self.context.get_fsuf()}"

    def v(self, name="w"):
        "generate new variable name."
        return f"{name}{self.context.get_vsuf()}"

    # new methods

    def func(self, num_args=1, var_name="w", params=None):
        """
        prepare for function generation.

        By default parameters are automatically generated from 'num_args' and 'var_name'.
        Alternatively you can explicitly specify them by 'params'.
        """
        self.entry_point = self.f()
        self.params_ = params or [self.v(name=var_name)
                                  for _ in range(num_args)]
        self.header_ = f"def {self.entry_point}({','.join(self.params_)}):\n"

        return self  # for chaining

    def comment(self, msg: str):
        "generate a general comment line."
        self.comment_ = f"# {msg}\n"

        return self

    def comment_tc(self, type_: Tree):
        "generate a comment line (typecheck)."
        self.comment(f"type check against '{reconstruct(type_)}'")

        return self

    def body(self, text):
        "set body text (possibly multi-lined)."
        if self.body_ == "" or self.body_.endswith("\n"):
            self.body_ += text
        else:
            self.body_ += ("\n" + text)

        return self

    def _gen_code(self) -> str:
        "create a function definition."
        before = self.header_ + indent(
            (self.comment_ or "# no comment\n") +
            (self.body_ or "pass"),
            ' ' * 2)
        logger.debug("before fix_code:\n%s", before)
        return fix_code(before)

    def code(self) -> CodeGenResult:
        "return generated code (and context)."
        return (Code(self._gen_code(), entry_point=self.entry_point), self.context)

    # old methods

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

    def comment_gen(self, type_: Tree):
        "generate a comment line (gen)."
        self.comment_ = f"# gen a value of '{reconstruct(type_)}'\n"

    def _comment_tc(self, type_: Tree):
        "(deprecated) generate a comment line (typecheck)."
        return f"# type check against '{reconstruct(type_)}'\n"

    def _body(self, text):
        "(deprecated) set body text (possibly multi-lined)."
        self.body_ = fix_code(text)


def markdown(code):
    "render code block using rich Markdown."
    md = Markdown("```python\n" + code.text + "```")
    return md
