> This README is draft and has some deprecated portions.
> See [docs/quickstart.md](./docs/quickstart.md) for the latest version.

# PyCheck: Python PBRT tool as refinement type checker

PyCheck is a tool for property-based random testing (PBRT) of Python programs.

This tool allows developers specifying property of a function, which is relation between input/output values, via refinement types like:

```
f: (x: int, y: { y:int | y > x }) -> { r:int | r > x and r > y }
```

Then it performs random testing; it randomly generates input values that satisfies their refinement types (`x0: int` and `y0: int` that is greater than `x0`), computes output of the function `r0 = f(x0, y0)`, and checks if it satisfies specified refinement type of the output (`r0: int` and `r0 > x0` and `r0 > y0`).
In other word tests are performed as a _test-based refinement type checking._ 

# Install

**Requirements:**

- Python 3.9+ (since PyCheck uses the latest type annotation mechanisms)
- SSH connection to https://github.ibm.com server. You need to register your SSH public key for your account.

To install, if you use pip, 

```bash
$ pip install git+ssh://git@github.ibm.com/SHINSA/pycheck.git@dev
```

See [docs/install.md](docs/install.md) for other package managers.


# Basic Usage

PyCheck is an advanced type checking tool like `mypy`.
Thus it is recommended to use PyCheck to programs that passes typechecking by `mypy`.

Install `mypy` and `pytest` by `pip install mypy pytest` (or install command that your package manager provides).

## Simply-typed functions

Let's look at a simply-typed function `inc()` in file `ex01.py`:

```python
# ex01.py
def inc(x: int) -> int:
    return x + 1
```

You can typecheck `inc()` using `mypy`:

```shell
$ mypy --strict ex01.py
Success: no issues found in 1 source file
```

While it's meaningless, you can also typecheck `inc()` using PyCheck. You need to write a test file `test_ex01.py` and a testcase `test_inc` that tests `inc()`.
`pycheck.check()` performs a random test and returns a boolean value if the given function is well-typed:

```python
# test_ex01.py
from pycheck import check


def inc(x: int) -> int:
    return x + 1


def test_inc():
    assert check(inc)  # typecheck inc() by a random test
```

Then you can start `pytest`:

```
$ pytest test_ex01.py
================================================= test session starts =================================================
platform darwin -- Python 3.9.5, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: ...
plugins: hypothesis-6.14.0
collected 1 item

test_ex01.py .                                                                                         [100%]

================================================== 1 passed in 0.38s ==================================================
```

By default, Pycheck randomly genetes 100 test cases by default. You can see what values are generated by turning logging on:

```
$ pytest test_ex01.py --log-cli-level=info
================================================= test session starts =================================================
platform darwin -- Python 3.9.5, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: ...
plugins: hypothesis-6.14.0
collected 1 item

test_ex01.py::test_inc
---------------------------------------------------- live log call ----------------------------------------------------
INFO     pycheck:__init__.py:26 testing <function inc at 0x10a6d4b80>
INFO     pycheck:__init__.py:30 signature = (x: int) -> int
INFO     pycheck.typecheck:typecheck.py:18 typecheck: term = inc, type = (x: int) -> int
INFO     pycheck.gen:gen.py:47 generating a value of type (x: int) -> int...
INFO     pycheck.gen:gen.py:47 generating a value of type <class 'int'>...
INFO     pycheck.gen:gen.py:140 generated value = 12
INFO     pycheck.gen:gen.py:140 generated value = {'x': 12}
INFO     pycheck.typecheck:typecheck.py:43 applying function...
INFO     pycheck.typecheck:typecheck.py:45 function application result = 13
INFO     pycheck.typecheck:typecheck.py:18 typecheck: term = 13, type = <class 'int'>
INFO     pycheck.typecheck:typecheck.py:20 context = {'x': 12}
INFO     pycheck.typecheck:typecheck.py:24 typed? = True
INFO     pycheck.typecheck:typecheck.py:49 test passed=1
...
INFO     pycheck.gen:gen.py:47 generating a value of type (x: int) -> int...
INFO     pycheck.gen:gen.py:47 generating a value of type <class 'int'>...
INFO     pycheck.gen:gen.py:140 generated value = 18
INFO     pycheck.gen:gen.py:140 generated value = {'x': 18}
INFO     pycheck.typecheck:typecheck.py:43 applying function...
INFO     pycheck.typecheck:typecheck.py:45 function application result = 19
INFO     pycheck.typecheck:typecheck.py:18 typecheck: term = 19, type = <class 'int'>
INFO     pycheck.typecheck:typecheck.py:20 context = {'x': 18}
INFO     pycheck.typecheck:typecheck.py:24 typed? = True
INFO     pycheck.typecheck:typecheck.py:49 test passed=100
INFO     pycheck.typecheck:typecheck.py:51 typed? = True (passed 100 tests.)
PASSED                                                                                                          [100%]

================================================== 1 passed in 0.58s ==================================================
```

You can see that:
- In the first testcase,
    - The generated value for `x` was `12`.
    - Function application `inc(x)` was computed with the generated input, which was `13`.
    - Applications result `13` was typechecked agaist `int`, which passed.
- 100 testcases were examined in total.

## Refinement-typed functions

Being different from `mypy`, PyCheck also can typecheck refinement-typed functions.

Let consider the `inc()` above. As you can see, the return value of `inc(x)` would be greater than its input `x`.
Thus the type of `inc()` can be **informally** written as follows:

```python
# ex02_informal.py
def inc(x: int) -> { r:int | r > x }:
    return x + 1
```

Here the type `{ r:int | r > x }` is called a *refinement type*, which means the type that contains values (say, `r`) whose types is `int` and satisfies `r > x`. Note that the value of the argument `x` can be used in the return type; so refinement types are also *dependent types*.

In PyCheck, the type above can be written as follows:

```python
# ex02.py
from pycheck import ArgsType, RefinementType, spec


@spec(ArgsType(x=int) >> RefinementType(int, 'r', lambda x, r: r > x))
def inc(x: int) -> int:
    return x + 1
```

where spec is the form of `@spec(<args type> >> <return type>)`. In this case, the first argument, `x`, should have type `int` and the return type should be a refinement type of `int`.

The first argument to `RefinementType` should be its base type, the second would be a parameter that is used in the third argument, which should be a predicate function.

> Note: I know the notation is ugly. Type notation would be subject to change.

By default, PyCheck typechecks a function with the type specified by `@spec`, otherwise with its type annotation.

## Conctract checking mode

Other than for typechecking, `@spec` can be used for describing a contract of the function. 
When the function is being called, its arguments and/or return values are dynamically checked and raises an error if they does not satisfy the contract specified by the `@spec`.

*(Note: This feature is not implemented yet. To appear.)*

# Customizing PyCheck

Environment variables to customize PyCheck:

- General
  - ...
- Parser
  - `PYCHECK_DEBUG_PARSER`: Turn on debug flag of parser for type annotation.

<!--
## Supported Types and Notations

`check()` only accepts non-lambda functions, where:
- Positional-only parameters are not used.

Supported types for each argument are:
- Base types (`int` and `str`),
- Tuple types (example: `Tuple[int, int]`),
- Refinement types expressed as `typing.Annotated` (example: `{x : int | x > 0}` can be expressed as `Annotated[int, lambda x: x > 0`]),
- Callable type (with refinement).

## Examples

Located under [examples](examples):

- ex01.py: example of a function that PASSES typecheck `f: int -> int`. 
- ex02.py: example of a function that FAILES typecheck `f: int -> int`.
- ex03.py: example of a function that PASSES typecheck `f: { x: int | x>0 } -> { x:int | x>=0 }`. 
- ex04.py: example of a function that FAILES typecheck `f: { x: int | x>=0 } -> { x:int | x>=0 }`. 
- ex05.py: example of a function that PASSES typecheck `f: str -> str`. 
- ex06.py: example of a multi-argument function (not tuple type argument) that PASSES typecheck `f: (int, int) -> str`. 

You can run these by:

```shell
python examples/<example file>
```

## Limitations

This version supports checking of function types `f: int -> int` and
simple (non-dependent) refinement types `f: { x:int | p(x) } -> { y:int | q(y) }`.

Here we encode refinement types as tuple: `(<type>, <refinement func>)`, where `<refinement func>` accept single argument of type `<type>`. Currently `<type>` should be `int`.

## TODO

Short term:
- Support dependent refinement types
- Supoort other types: especially, multi-arguments func and container types, pandas types
- Show counterexample
- Show statistics
- Implement optimization

Long term:
- Support contract annotation
- Implement shrinking
-->