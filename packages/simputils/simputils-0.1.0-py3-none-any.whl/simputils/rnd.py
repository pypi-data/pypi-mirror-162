from random import randrange


def get_random_int_excluding(maximum, excluding):
    value = randrange(maximum)
    while value in excluding:
        value = randrange(maximum)
    return value
