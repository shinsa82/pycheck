from inspect import getclosurevars
from pprint import pprint

v = 1


def define_g1():
    z = 5

    def g(x, y):
        o = v + w + x + y + z
        return o

    return g


def define_g2():
    z = 5

    g = lambda x, y: v + w + x + y + z

    return g


def define_g3():
    z = 5

    g = eval('lambda x, y: v + w + x + y + z')

    return g


def define_g4():
    z = 5

    g = eval('lambda x, y: v + w + x + y + z', globals(), locals())

    return g


my_global = {'v': 11}


def define_g5():
    z = 5

    g = eval('lambda x, y: v + w + x + y + z', my_global, {'z': 15})

    return g


f1 = define_g1()
pprint(getclosurevars(f1))
# pprint(f1.__globals__)

f2 = define_g2()
pprint(getclosurevars(f2))
# pprint(f2.__globals__)

f3 = define_g3()
pprint(getclosurevars(f3))
# pprint(f3.__globals__)

f4 = define_g4()
pprint(getclosurevars(f4))
# pprint(f4.__globals__)

f5 = define_g5()
pprint(getclosurevars(f5))
# pprint(f5.__globals__)

# w = 1
# z = 1
# f5(1, 2)


my_global |= {'w': 10, 'z': 15}
print(f5(1, 2)) # v(11) + w(10) + x(1) + y(2) + z(15) = 39
