import random


def test_seed():
    BITS = 64
    MAX = 0x8000_0000
    LEN = 10
    seed = random.getrandbits(BITS)
    print(f"{seed=}")
    print(f"{hex(seed)=}")
    r1 = random.Random(seed)
    r2 = random.Random(seed)
    l1 = [r1.randrange(MAX) for i in range(LEN)]
    l2 = [r2.randrange(MAX) for i in range(LEN)]
    print(f"{l1=}")
    print(f"{l2=}")
    assert l1 == l2
