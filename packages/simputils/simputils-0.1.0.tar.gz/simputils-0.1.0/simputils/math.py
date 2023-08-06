import math


def sign(value):
    if value == 0:
        return abs(value)
    return math.copysign(1, value)
