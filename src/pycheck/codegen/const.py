"classes and constants."
from dataclasses import dataclass, replace
from typing import TypeAlias

from autopep8 import fix_code


@dataclass
class Code:
    """
    Code to be executed by typechecker.

    Code text is formatted using 'fix_code()' of autopep8.
    'entry_point' is the name of the function that is entry point of the code.
    It means, the code text would be as follows:
    ```
    def <entry_point>(...):
        ...
    ```
    """
    text: str = ""
    entry_point: str = None

    def __str__(self):
        return self.text

    def __post_init__(self):
        "post initialization"
        self.text = fix_code(self.text)

    def fix_code(self, options=None):
        "format the code using autopep8."
        new_text = fix_code(self.text, options=options)
        return replace(self, text=new_text)

    def add_line(self, line: str):
        "add a line to existing code."
        # self.text += "\n"
        self.text += line
        self.fix_code()

    def append(self, other: "Code") -> "Code":
        return Code(self.text + other.text).fix_code()

    def exec(self):
        "executing code and change the environment."
        raise NotImplementedError()


@dataclass
class CodeGenContext:
    "stores context to be brought around for generating code."
    func_suffix: int = 0  # used when generating function name
    var_suffix: int = 0  # used when generating variable name

    def get_fsuf(self):
        "get func suffix and increment count."
        ret: int = self.func_suffix
        self.func_suffix += 1
        return ret

    def get_vsuf(self):
        "get var suffix and increment count."
        ret: int = self.var_suffix
        self.var_suffix += 1
        return ret


CodeGenResult: TypeAlias = tuple[Code, CodeGenContext]
