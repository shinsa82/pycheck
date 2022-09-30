"Generates parser that parses reftype."
from logging import getLogger
from pathlib import Path

from environs import Env
from lark import Lark

logger = getLogger(__name__)
GRAMMAR: Path = Path(__file__).parent / 'reftype.lark'
_env = Env()


def gen_parser() -> Lark:
    "generate a parser for reftype."
    with _env.prefixed('PYCHECK_'):
        debug: bool = _env.bool('DEBUG_PARSER', False)
        logger.info('reftype parser configuration: debug flag = %s', debug)

        # (dynamic) earley parser cannot use priorities on terminals,
        # which is used in common/python.lark.
        with open(GRAMMAR, mode='r', encoding='utf-8') as f:
            _parser: Lark = Lark(
                f,
                parser='earley',
                lexer='standard',
                debug=debug,
                ambiguity='explicit',
                propagate_positions=True,
            )
            return _parser


parser: Lark = gen_parser()
