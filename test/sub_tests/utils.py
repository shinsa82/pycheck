"test utilities."
from rich import print  # pylint: disable=redefined-builtin
from rich.markdown import Markdown

from pycheck import Config
from pycheck.executor import evaluate, execute

# pylint:disable=invalid-name


def exec_code(code, val, is_typed):
    "subroutine for test."
    # locals_ = {}

    # render code block using rich Markdown
    md = Markdown("```python\n" + code.text + "```")
    print("code:")
    print(md)

    f = evaluate(code)
    # execute typechecking only once
    res = execute(f, term=val, config=Config(max_iter=1))
    print(res)

    assert res.well_typed == is_typed
