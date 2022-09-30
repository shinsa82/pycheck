# Introduction of PyCheck architecture and development resources

Here *"reftype"* means refinement types.


## How to typecheck terms

For example, type check of a term `t` against a type `T` will be performed by calling `typecheck` method of PyCheck:

```python
b: bool = typecheck(t, T)
```

If the term is well-typed, `True` will be returned. Otherwise `False` will be returned.
If you want the detail of the typechecking, specify the `detail` keyword option:

```python
result: Result = typecheck(t, T, detail=True)
b: bool = result.well_typed
```

Example:

```python
def Max(x:int, y:int) -> int:
    return (x if x >= y else y)

b: bool = typecheck(Max, "(x:int) -> (y:int) -> {r:int | r >= x and r >= y}")
```

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
