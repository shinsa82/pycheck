from pprint import pprint


def main():
    # in main's local scope
    l1 = locals()
    w: int = 3
    l2 = locals()
    pprint(l1)
    pprint(l2)
    pprint(locals())

main()
