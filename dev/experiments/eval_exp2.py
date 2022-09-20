g = globals()
print(g)
l = {'y': 3}
print(globals())
f = eval('lambda x: y+x', g)
f(3)

try:
    f = eval('lambda x: y+x', g)
    print(f(3))
except NameError as e:
    print('error')

try:
    g = eval('lambda x: y+x', g, l)
    print(g.__closure__)
    y = 3
    print(g(3))
except NameError as e:
    print('error')

try:
    h = eval('lambda x: y+x', l)
    print(h.__closure__)
    print(h(3))
except NameError as e:
    print('error')

try:
    h = eval('lambda x: y+x', l)
    print(h.__closure__)
    h(3)
except NameError as e:
    print('error')
