# Introduction of PyCheck architecture and development resources

Here *"reftype"* means refinement types.

## Install 

> You need to use **Python 3.10** (probably it works on 3.9, but I'm not sure).

You can directory install from repository:

```
pip install git+https://github.com/shinsa82/pycheck.git
```

Or clone the repo and install it:

```
git clone https://github.com/shinsa82/pycheck.git
pip install [-e] pycheck
```

You can check the version of installation

```
$ pip list
...
pycheck          0.5.0
...
```

and if importing would be successful:

```
$ python
Python 3.10.7 (main, Oct  5 2022, 14:33:54) [GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pycheck
>>> pycheck.__version__
'0.5.0'
```

## Example codes

See and execute [test_main.py](../test/test_main.py).
If you want to run a specific testcase, specify its name pattern by `-k` option:

```bash
pip install pytest
pytest test/test_main.py [-k func_5]
```


## How to typecheck terms

For example, type check of a term `t` against a type `T` will be performed by calling `typecheck` method of PyCheck:

```python
b: bool = typecheck(t, T)
```

If the term is well-typed, `True` will be returned. Otherwise `False` will be returned.
If you want the detail of the type checking, specify the `detail` keyword option:

```python
result: Result = typecheck(t, T, detail=True)
b: bool = result.well_typed
```

Example: currently only unary function is supported, you need to define n-ary function using a tuple:

```python
def Max(p: tuple[int, int]) -> int:
    return (p[0] if p[0] >= p[1] else p[1])

b: bool = typecheck(Max, "p:(x:int * int) -> {r:int | r >= p[0] and r >= p[1]}")
```

> Note that `x:int * int` here denotes a dependent product `(x:int) * int` and you can write it as the latter for readability.

## Annotation to function

If you want to type check a function, you can annotate its type using the `@reftype` decorator:

```python
@reftype("(x:int) -> (y:int) -> {r:int | r >= x and r >= y}")
def Max(x:int, y:int) -> int:
    return (x if x >= y else y)
```

The decorator stores the reftype into an attribute of the target function.

```python
Max.__pycheck_reftype__ = RefType("(x:int) -> (y:int) -> {r:int | r >= x and r >= y}", ...)
```

In this case, you just call `typecheck()` without its type:

```python
b: bool = typecheck(Max)
```

## Internal

Internally it generates a type-checking code and repeat execution of it over and over.

```python
def typecheck(term, typ=None, detail=False):
    # here, term has been valuated to a value.

    # RefType holds the parsed representation of the reftype string.
    reftype: RefType = term.__pycheck_reftype__  or RefType(typ)

    code: Code = reftype.gen_code()
    result: Result = execute(code, config)
    return result if detail else result.well_typed
```

RefType class parses the given reftype string into parse tree using [Lark](https://github.com/lark-parser/lark) parser.

```python
class RefType:
    def __init__(self, type: str):
        self.type = type_str
        self.parse_tree = self.parse(self.type_str)
```

`RefType.gen_code()` generates a Python code (at the point of writing, it is string) where safety of its execution is equiavlent to well-typedness of the original term.
