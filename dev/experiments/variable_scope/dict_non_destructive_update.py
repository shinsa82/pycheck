a: dict = {'a': 3, 'b': 4}
b: dict = {'c': 5, 'd': []}
c: dict = a | b

print(a)
print(b)
print(c)
assert c['d'] is b['d']  # 同じオブジェクトを指す

c['c'] = 0
print()
print(b)  # c の変更は b に伝搬しない
print(c)

b['d'] = 0
print()
print(b)
print(c)  # b の変更は c に伝搬しない
