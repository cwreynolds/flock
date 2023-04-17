#------------------------------------------------------------------------------
#
# Utilities.py -- new flock experiments
#
# Utility functions
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#------------------------------------------------------------------------------

import numpy as np
from Vec3 import Vec3


def interpolate(alpha, p, q):
    return (p * (1 - alpha)) + (q * alpha)

# TODO 20230409 temporary, to be replaced by RandomSequence.
def frandom01():
    return np.random.uniform(0, 1)
def frandom2(a, b):
    return interpolate(frandom01(), a, b)
# TODO can't even deside what they are called:
def random01(): return frandom01()
def random2(a, b): return frandom2(a, b)

# Constrain a given value "x" to be between two bounds: "bound0" and "bound1"
# (without regard to order). Returns x if it is between the bounds, otherwise
# returns the nearer bound.
def clip(x, bound0, bound1):
    clipped = x
    minimum = min(bound0, bound1)
    maximum = max(bound0, bound1)
    if clipped < minimum:
        clipped = minimum
    if clipped > maximum:
        clipped = maximum
    return clipped

# Normalize by clipping, same as clip(x, 0, 1)
def clip01 (x):
    return clip(x, 0, 1)

# True when x is between given bounds.
def between(x, a, b):
    return (min(a, b) <= x) and (x <= max(a, b))

# True when a and b differ by no more than epsilon.
def within_epsilon(a, b, epsilon):
    return abs(a - b) <= epsilon

# Takes a 32 bit value and shuffles it around to produce a new 32 bit value.
# "Robert Jenkins' 32 bit integer hash function" from "Integer Hash Function"
# (1997) by Thomas Wang (https://gist.github.com/badboy/6267743)
# Fiddled to make it work like 32 bit in Python.
def rehash32bits(int32):
    ones = 0xffffffff  # 32 bits of all ones.
    int32 = ones & int32
    int32 = ones & ((int32 + 0x7ed55d16) + (int32 << 12))
    int32 = ones & ((int32 ^ 0xc761c23c) ^ (int32 >> 19))
    int32 = ones & ((int32 + 0x165667b1) + (int32 <<  5))
    int32 = ones & ((int32 + 0xd3a2646c) ^ (int32 <<  9))
    int32 = ones & ((int32 + 0xfd7046c5) + (int32 <<  3))
    int32 = ones & ((int32 ^ 0xb55a4f09) ^ (int32 >> 16))
    return int32

# class RandomSequence
# Vec3 randomUnitVector();
# does Python allow the trick where RandomSequence is defined one
# place but RandomSequence::randomUnitVector() is defined elsewhere?
# oh, maybe yes: https://stackoverflow.com/a/2982/1991373

# Generate a random point in an axis aligned box, given two opposite corners.
def random_point_in_axis_aligned_box(a, b):
    return Vec3(random2(min(a.x, b.x), max(a.x, b.x)),
                random2(min(a.y, b.y), max(a.y, b.y)),
                random2(min(a.z, b.z), max(a.z, b.z)))

# Generate a random point inside a unit diameter disk centered on origin.
def random_point_in_unit_radius_sphere():
    v = None
    while True:
        v = random_point_in_axis_aligned_box(Vec3(-1, -1, -1), Vec3(1, 1, 1))
        if v.length() <= 1:
            break
    return v;

# Generate a random unit vector.
def random_unit_vector():
    v = None
    m = None
    while True:
        v = random_point_in_unit_radius_sphere()
        m = v.length()
        if m > 0:
            break
    return v / m;


@staticmethod
def unit_test():
    assert clip01(1.5) == 1
    assert clip01(0.5) == 0.5
    assert clip01(-1) == 0
    assert clip(0, 1, 5) == 1
    assert clip(1.5, 1, 5) == 1.5
    assert clip(0, -1, -5) == -1
    assert between(0, 1, 2) == False
    assert between(1.5, 1, 2) == True
    assert between(1.5, 2, 1) == True
    assert between(0, -1, 1) == True
    assert between(-2, 1, -1) == False
    assert within_epsilon(1, 1, 0)
    assert within_epsilon(1.1, 1.2, 0.2)
    assert within_epsilon(-1.1, -1.2, 0.2)
    assert not within_epsilon(1.1, 1.2, 0.01)
    assert rehash32bits(2653567485) == 1574776808
    # TODO 20230409 test random-number utilities, later RandomSequence.
