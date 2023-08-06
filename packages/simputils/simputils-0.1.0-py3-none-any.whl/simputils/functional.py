def identity(x):
    return x


class Mutable:
    """
    Mutable wrapper of an immutable object.
    Stores an object which allows to set and get it.
    Typical usecase is the following pattern:

    exec(a, f)

    Where:
    - 'exec' is an external library function which doesn't return anything
    - 'a' is an immutable object
    - 'f' is a user function that returns an object of 'type(a)'

    This class helps in transferring the return value of 'f' via Mutable(a).
    Using the following pattern:

    exec(Mutable(a), f')

    Where:
    f'(ms: Mutable) := x.set(f(x.get()))
    """

    def __init__(self, x):
        self.x = x

    def set(self, x):
        self.x = x

    def get(self):
        return self.x
