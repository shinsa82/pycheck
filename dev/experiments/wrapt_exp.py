import logging
from inspect import signature
from typing import Any, Union

from wrapt import decorator

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {filename}:{lineno}:{funcName}: {message}", style="{"
)


def deco(**kwargs):
    """experiment: a logging decorator"""
    logging.info(kwargs)
    return lambda x: x


@deco(x=int)  # with argument(s). dict with key 'x' will be passed to deco.
def foo(x: int) -> int:
    return x * 2 + 1


@deco()  # without arguments but with paren. empty dict will be passed to deco.
def bar(x: int) -> int:
    return x * 2 + 1


try:
    # without arguments nor paren. bar will be passed to deco,
    # as the first positional arg. it causes an error.
    @deco
    def baz(x: int) -> int:
        return x * 2 + 1
except:
    logging.exception('error')

print(foo(1))

#
# practice of wrapt.decorator
#


def qoo(**kwargs_):
    logging.info("parameters are:")
    logging.info(kwargs_)

    @decorator
    def wrapper(wrapped, instance, args, kwargs):
        logging.info(f"args = {args}")
        logging.info(f"kwargs = {kwargs}")
        return wrapped(*args, **kwargs)
    return wrapper


@qoo(x=Union[int, None])
def qox(x: int) -> int:
    return x * 2 + 1


def qox_raw(x: int) -> int:
    return x * 2 + 1


print(qox(1))
print(qox(x=1))

logging.info(signature(qox))
logging.info(signature(qox_raw))

# cannot use "return" as parameter name
# def f(return):
#     return return


class ArgsType(metaclass=type):
    def __init__(self, **kwargs):
        super().__init__()
        self.args_type = kwargs

    def __str__(self):
        return f"ArgsType({self.args_type})"

    def __rshift__(self, return_type):
        return FunctionType(self, return_type)


class FunctionType(metaclass=type):
    def __init__(self, args_type, return_type):
        self.args_type = args_type
        self.return_type = return_type

    def __str__(self):
        return f"FunctionType({self.args_type} -> {self.return_type})"


args = ArgsType
logging.info(args(x=int, y=str))


def spec(type: FunctionType, check_argtype=False):
    """decorator that specifies function sigunature of the decorated using refinement types"""
    logging.info("spec (= type) of the function:")
    logging.info(type)
    logging.info(f"type check arguments when invoked? = {check_argtype}")

    @decorator
    def wrapper(wrapped, instance, args, kwargs):
        logging.info("in the wrapper. show patched attributes...")
        logging.info(f"{wrapped._type=}")
        logging.info(f"{wrapped._check_argtype=}")
        if wrapped._check_argtype:
            logging.info("typechecking arguments...")
        return wrapped(*args, **kwargs)

    def wrapping(wrapped):
        logging.info(f"monkeypatching function {wrapped}")
        wrapped._type = type
        wrapped._check_argtype = check_argtype
        f = wrapper(wrapped)
        return f

    return wrapping


@spec(FunctionType(args(x=int, y=int), int))
def foobar1(x, y):
    return x + y + x * y


@spec(FunctionType(None, None), check_argtype=True)
def foobar2(x, y):
    return x + y + x * y


@spec(args(x=int, y=int) >> int)
def foobar3(x, y):
    return x + y + x * y


logging.info(foobar1(2, 3))
logging.info(foobar2(2, 3))
logging.info(foobar3(2, 3))


def typecheck(func) -> bool:
    if hasattr(func, '_type'):
        logging.info(f"function spec found: {func._type}")
        logging.info("typechecking...")
        return True
    raise ValueError(
        f'function {func} has not specification. To typecheck, specify it with @spec decorator.')


try:
    typecheck(qox)
except:
    logging.exception('error caught')

typecheck(foobar1)
