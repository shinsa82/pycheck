"""
Opcode classes and an Evaluator.

Type-checking code is expressed as a list of opcodes.
The opcode list will be processed, optimized and executed.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from inspect import Signature, signature
from operator import attrgetter, itemgetter
from pprint import pformat
from textwrap import indent
from typing import Any, Callable, Iterable, Protocol

from humanize.time import precisedelta

from pycheck.type import Type

from .config import Config
from .util import get_logger

debug, info, warning, error, exception = get_logger(__name__)


class AssumeException(Exception):
    """
    Exception that will be raised when Assume fails.
    If raised, the typechecker retries data generation.
    """
    pass


class AssertException(Exception):
    """
    Exception that will be raised when Assert fails.
    If raised, the typechecker aborts. (typecheck fails)
    """
    pass


@dataclass
class OpCode(Protocol):
    "Opcode base class"
    addr: int = -1  # address (= line no) of this OpCode, which starts from 0.

    def evaluate(self, ev: "Evaluator") -> Any:
        ...


OpCodes = Iterable[OpCode]


def project(context: dict[str, Any], args: Iterable[str]) -> dict[str, Any]:
    "restrict domain of a context to args"
    return {k: v for k, v in context.items() if k in args}


@dataclass
class Gen(OpCode):
    var: str = None
    type_: Type = None
    impl: Callable = None  # generator implementation.

    def evaluate(self, ev: "Evaluator") -> Any:
        debug(f'generating a value of type {self.type_.type_name}')
        ev.context[self.var] = self.impl()


@dataclass
class Apply(OpCode):
    "function application and assignment of the result."
    # variable name of function. autual function value needs to be obtained from context.
    func: Any = None
    args: Any = None
    to: str = None  # variable assigned to
    # signature: Signature = None  # signature of the func

    # def __post_init__(self):
    #     "post initializer"
    #     self.signature = signature(self.func)

    def evaluate(self, ev: "Evaluator") -> None:
        context = ev.context
        f = context[self.func]  # actual func.
        debug(signature(f))
        ctx = project(context, signature(f).parameters.keys())
        debug(f"restricted context = {ctx}")
        res = f(**ctx)
        context[self.to] = res


@dataclass
class Assign(OpCode):
    "normal (= not data gen) assignment."
    to: str = None  # variable assigned to
    exp: Any = None

    def evaluate(self, ev: "Evaluator") -> Any:
        ev.context[self.to] = self.exp


@dataclass
class IsIns(OpCode):
    """
    Opcode for isinstance(v, t).
    """
    v: Any = None
    type_: Type = None
    # if not None, this function is used to instance check.
    func: Callable = None

    def evaluate(self, ev: "Evaluator") -> Any:
        context = ev.context
        if self.func is not None:
            b = self.func(context[self.v])
        else:
            b = isinstance(context[self.v], self.type_)
        debug(f"evaluated = {b}")
        if not b:
            raise AssertionError(f'assertion failed at {self}')


@dataclass
class TC_(OpCode):
    "for debug; opcode for typechecking."
    v: Any = None
    type_: Type = None


@dataclass
class Assert_(OpCode):
    """
    for debug; opcode for assertion against predicate.

    Entire code fails if the predicate is not satisfied.
    """
    bind: tuple[str, str] = None  # variable binding of a value to base_var.
    pred: Any = None
    sig: Signature = None

    def __post_init__(self):
        # debug(self.pred)
        self.sig = signature(self.pred)

    def evaluate(self, ev: "Evaluator") -> Any:
        debug(
            f'asserting refinement {self.pred} (signature = {self.sig}) with binding {self.bind}...')
        bind_to, bind_from = self.bind
        new_context = project(
            ev.context | {bind_to: ev.context[bind_from]}, self.sig.parameters.keys())
        debug(f"new context = {new_context}")
        satisfied = self.pred(**new_context)
        if ev.config.stat:
            ev.stat.record(
                self.addr, {'kind': 'assert', 'addr': self.addr, 'value': new_context[bind_to], 'satisfied': satisfied, 'context': new_context})
        if satisfied:
            debug('assertion statisfiled')
        else:
            # warning('assertion unsatisfied!')
            raise AssertionError(
                f'assertion unsatisfied at {self} with context {new_context}')


@dataclass
class Assume_(OpCode):
    """
    for debug; opcode for assumption against predicate.

    Retry entire (or partial) code if the predicate is not satisfied.
    """
    bind: tuple[str, str] = None  # variable binding of a value to base_var.
    pred: Any = None
    sig: Signature = None

    def __post_init__(self):
        # debug(self.pred)
        self.sig = signature(self.pred)

    def evaluate(self, ev: "Evaluator") -> Any:
        debug(
            f'calling refinement {self.pred} (signature = {self.sig}) with binding {self.bind}...')
        # debug(getsource(self.pred)) # OSError, at least, for lambda
        # context = ev.context
        # to_name, from_name = self.bind
        # binds = {to_name: ev.context[from_name]}
        # debug(f'resolved binding: {binds}')
        # new_context = context | binds
        new_context = project(ev.context, self.sig.parameters.keys())
        debug(f"new context = {new_context}")
        assert self.bind[0] == self.bind[1]
        base_var = self.bind[0]
        satisfied = self.pred(**new_context)
        if ev.config.stat:
            ev.stat.record(
                self.addr, {'kind': 'assume', 'addr': self.addr, 'value': ev.context[base_var], 'satisfied': satisfied,
                            'context': new_context})
        if satisfied:
            debug('refinement statisfiled')
        else:
            debug('refinement unsatisfied!')
            raise AssumeException(f'refinement unsatisfied at {self}')


@dataclass
class Move(OpCode):
    """
    Move (or rename) variables.
    """
    from_: str = None
    to: str = None

    def evaluate(self, ev: "Evaluator") -> Any:
        debug(f'moving value from "{self.from_}" to "{self.to}"...')
        context = ev.context
        context[self.to] = context[self.from_]
        del context[self.from_]


# class Or(OpCode):
#     "Opcode for an 'or' operator. It shortcuts evaluation."

#     def __init__(self, l: OpCode, r: OpCode) -> None:
#         self.l = l
#         self.r = l

#     def __str__(self) -> str:
#         return f"Or({self.l}, {self.r})"

#     def __repr__(self) -> str:
#         return str(self)

#     def evaluate(self, ex: "Evaluator") -> bool:
#         b = ex.evaluate([self.l]) or ex.evaluate([self.r])
#         info(f"evaluated = {b}")
#         return b


class Result(Enum):
    NA = auto()  # typecheck not finished
    OK = auto()
    FAIL = auto()
    TIMEOUT = auto()


@dataclass
class Statistics:
    """
    Class for storing statistical data during opcode execution.
    Note that this object is not reusable: if you want to execute at the second time,
        re-create this object.
    """
    config: Config = None
    result: Result = Result.NA

    tries: int = 0  # total number of execution runs.
    success_: int = 0  # number of success runs (= executed to the end).
    retry_: int = 0  # number of runs where assume failed.
    fail_: int = 0  # number of runs where assert failed (max = 1).

    start_: datetime = None
    end_: datetime = None

    # detail: dict = field(
    #     default_factory=lambda: defaultdict(list))
    detail: list[Any] = field(default_factory=lambda: [])

    def start(self):
        "start execution of runs."
        self.start_ = datetime.now()

    def end(self, result):
        "end execution of runs."
        self.end_ = datetime.now()
        self.result = result

    def start_run(self) -> None:
        "start one run."
        self.tries += 1

    def success(self) -> None:
        self.success_ += 1

    def retry(self) -> None:
        self.retry_ += 1

    def fail(self) -> None:
        self.fail_ += 1

    def need_to_run(self) -> bool:
        return self.tries < self.config.max_tries

    def progress(self) -> str:
        return f'({self.success_}/{self.config.max_iteration})'

    def finished(self) -> bool:
        return self.success_ == self.config.max_iteration

    def elapsed(self) -> timedelta:
        return self.end_ - self.start_

    def _overview_header(self) -> str:
        if self.result == Result.OK:
            return '[OK] typecheck succeeded!'
        elif self.result == Result.FAIL:
            return '[FAIL] typecheck failed. (= ill-typed)'
        elif self.result == Result.TIMEOUT:
            return f'[TIMEOUT] typecheck aborted. exceeded max tries ({self.config.max_tries}).'
        else:
            raise ValueError(
                'overview is not defined until execution will be finished.')

    def overview(self) -> str:
        "return overview string of the execution"
        ret = self._overview_header() + '\n'
        ret += indent("\n".join(
            [f'# tries: {self.tries}',
             f'# successes: {self.success_}',
             f'# failed assumptions: {self.retry_}',
             f'# failed assertions: {self.fail_}']), '  ')
        ret += f'\nelapsed time: {precisedelta(self.elapsed(), minimum_unit="milliseconds", format="%0.3f")}'
        return ret

    def record(self, addr: int, obj: Any) -> None:
        "records items to execution stats. (assume, assert, branch, performance, ...)"
        # l = self.detail[addr]
        # l.append(obj)
        self.detail.append(obj)  # assumes that addr is in obj


class Evaluator:
    """
    executor of opcodes.
    """
    context: dict[str, Any]
    stat: Statistics

    def __init__(self, config: Config = None) -> None:
        self.context = {}
        self.config = config or Config()
        info(f"Evaluator {self} initialized")

    def evaluate(self, opcodes: OpCodes, config: Config = None) -> Statistics:
        """
        iterating opcodes execution until it finish or timout execution.
        """
        if config:
            self.config = config
        self.stat = Statistics(config=self.config)

        # preprocess to backtrack
        debug('collecting Gen and Assume nodes...')
        gens = list(filter(lambda o: isinstance(o, Gen), opcodes))
        debug(pformat(gens))
        gen_addrs = list(map(attrgetter('addr'), gens))
        debug(f'generator addresses: {gen_addrs}')
        assumes =  list(filter(lambda o: isinstance(o, Assume_), opcodes))
        ass_addrs = list(map(attrgetter('addr'), assumes))
        debug(f'assume addresses: {ass_addrs}')
        bt = {ass: list(filter(lambda g: g<ass, gen_addrs)) for ass in ass_addrs}
        debug(f'backtracking candidates table: {bt}')
        info('')
        info('starting iteration of opcodes execution...')
        info(f'  opcode length = {len(opcodes)}')
        info(f'  max iteration = {self.config.max_iteration}')
        info(f'  max tries = {self.config.max_tries}')
        print('')
        print('starting typechecking iteration...')
        self.stat.start()

        while self.stat.need_to_run():
            try:
                self.stat.start_run()
                info('')
                info(
                    f'#{self.stat.tries}: evaluating opcodes... {self.stat.progress()}')
                self.context = {}
                for opcode in opcodes:
                    info('-' * 10)
                    info(f"executing {opcode=}")
                    opcode.evaluate(self)
                    info(f'context: {self.context}')
                info('opcodes are executed to end. one pass of typecheck passed.')
                self.stat.success()
                if self.stat.finished():
                    self.stat.end(Result.OK)
                    info('')
                    info(self.stat.overview())
                    print()
                    print(self.stat.overview())
                    return self.stat
            except AssumeException as e:
                debug(e)
                info('assumption failed. retrying execution.')
                self.stat.retry()
            except AssertionError as e:
                self.stat.fail()
                self.stat.end(Result.FAIL)
                warning(e)
                warning('')
                warning(self.stat.overview())
                print('')
                print(self.stat.overview())
                return self.stat

        self.stat.end(Result.TIMEOUT)
        warning('')
        warning(self.stat.overview())
        print('')
        print(self.stat.overview())
        return self.stat


__all__ = ['IsIns', 'Or', 'Evaluator']
