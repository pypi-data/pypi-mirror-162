from collections import defaultdict
from itertools import chain, filterfalse, groupby, islice, zip_longest

from more_itertools import flatten

from .functional import identity


def is_sorted(iterable, key=identity):
    sentinel = object()
    iterable_shifted = iter(iterable)
    if next(iterable_shifted, sentinel) is sentinel:
        return True  # empty iterable
    return all(key(a) <= key(b) for a, b in zip(iterable, iterable_shifted))


def all_equal(iterable, key=identity):
    g = groupby(iterable, key)
    return next(g, True) and not next(g, False)


def split_elements(iterable, key=identity):
    """
    Return an iterable of lists.
    Each list contains elements which are considered equal according to the key.
    This algorithms can be used to split elements which are not sortable"""
    mappings = defaultdict(list)
    for e in iterable:
        mappings[key(e)].append(e)
    return flatten(mappings.values())


def max_dist_indices_impl(low, high):
    if abs(low - high) <= 1:
        yield low
        if low != high:
            yield high
        return

    split_point = (low + high) // 2
    yield split_point
    lower_dist = (split_point - 1) - low
    upper_dist = high - (split_point + 1)
    lower_half = max_dist_indices_impl(low, split_point - 1)
    upper_half = max_dist_indices_impl(split_point + 1, high)

    if lower_dist > upper_dist:
        yield from filterfalse(
            lambda x: x is None, chain(*zip_longest(lower_half, upper_half))
        )
        return
    yield from filterfalse(
        lambda x: x is None, chain(*zip_longest(upper_half, lower_half))
    )


def max_dist_indices(n):
    """Generates a sequence of indices up to `n`.
    The indices are sequenced to be as distant as possible
    from any other previously generated index.

    E.g.
    n == 11,
    A possible sequence conforming this property is:
    0, 10, 5, 3, 7, 2, 8, 1, 4, 6, 9
    """
    if n == 0:
        return
    if n == 1:
        yield 0
        return

    yield 0
    yield n - 1
    yield from max_dist_indices_impl(1, n - 2)


def rangify(sorted_integer_sequence):
    """
    Turns a list of sorted integers into a list of range definitions.
    Duplicates are not allowed.

    E.g.
    [1, 2, 3, 7, 8, 10, 11]
    Becomes

    [range(1, 4), range(7, 9), range(10, 12)]
    """

    assert is_sorted(sorted_integer_sequence)
    assert len(sorted_integer_sequence) == len(set(sorted_integer_sequence))

    ranges = []
    current_start = sorted_integer_sequence[0]
    for i, j in zip(sorted_integer_sequence, islice(sorted_integer_sequence, 1, None)):
        if j == i + 1:
            continue
        else:
            ranges.append(range(current_start, i + 1))
            current_start = j

    ranges.append(range(current_start, sorted_integer_sequence[-1] + 1))

    return ranges


def inverse_ranges(ranges, start=None, stop=None):
    """
    Takes the inverse of a list of ranges.
    The result is a list of ranges, not contained in the given list.
    By default the start is the start of the first range.
    By default the stop is the stop of the last range.
    The given list of ranges should be sorted and non-overlapping.
    """
    assert is_sorted(ranges, key=lambda r: (r.start, r.stop))

    if start is None:
        start = ranges[0].start
    if stop is None:
        stop = ranges[-1].stop

    inverse_ranges = []
    for r in ranges:
        if start >= r.stop:
            continue
        if stop <= r.start:
            break

        if r.start - start > 0:
            inverse_ranges.append(range(start, r.start))

        start = r.stop

    if start < stop:
        inverse_ranges.append(range(start, stop))

    return inverse_ranges
