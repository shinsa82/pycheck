from pprint import pprint

x0 = 8
x1 = 5

# def inner1():
#     "no env"
#     x = 3
#     return eval('lambda y: x + y')


# def inner2():
#     "with global env"
#     x = 3
#     return eval('lambda y: x + y', globals())

def f(x):
    print('-- f(x) --')
    z = x + x0  # contains a free variable'x0', but its in a global scope.
    pprint(locals())
    pprint(globals())


# show function's globals and closures
print('f.globals')
pprint(f.__globals__)
print('f.closure')
pprint(f.__closure__)

f(3)

#####


def g(x):
    print('-- g(x) --')
    z = x + x0  # contains a free variable'x0', but its in a global scope.

    def h(x):
        print('-- h(x) --')
        print(z) # point to outer local scope
        pprint(locals())
        pprint(globals())

    pprint(locals())
    pprint(globals())

    return h


h = g(3)

# show function's globals and closures
print('======== h info =========')
print('h.globals:')
pprint(h.__globals__)
print('h.closure:')
pprint(h.__closure__)
pprint(dir(h.__closure__[0]))
pprint(h.__closure__[0].cell_contents)
pprint(h.__code__)
print(h.__code__.co_nlocals)
print(h.__code__.co_names)
print(h.__code__.co_argcount)
print(h.__code__.co_varnames)
print(h.__code__.co_freevars)
print(h.__code__.co_cellvars)
print(h.__code__.co_consts)
h(3)


def inner3():
    "also with local env"
    x = 3
    pprint(locals())
    pprint(globals())
    return eval('lambda y: x + y', globals(), locals())


# try:
#     f = inner1()
#     pprint(f)
#     print(f(5))
# except NameError as e:
#     print(e)

# try:
#     f2 = inner2()
#     pprint(f2)
#     print(f2(5))
# except NameError as e:
#     print(e)
f3 = inner3()
pprint(f3)
print(f3(5))

pprint(locals())
pprint(globals())


def f(x2):
    x3 = x1 + x2
    print('-' * 10)
    pprint(locals())
    pprint(globals())

    def g(x4):
        x5 = x3 + x2
        print('-' * 10)
        pprint(locals())
        pprint(globals())
    g(7)


f(2)
