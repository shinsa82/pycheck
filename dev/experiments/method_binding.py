"method binging experiment."


class C:
    x: int

    def __init__(self, x_init: int) -> None:
        self.x = x_init

    def add_print_x(self, y: int) -> int:
        z = self.x + y
        print(f"{z=}")
        return z


# you can call a method just as a (bound) function.
c = C(x_init=3)
m = c.add_print_x  # m is a method, not a function
m(4)  # to be 7
