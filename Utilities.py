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

# This value works on my laptop with Python 3.10
epsilon = 0.00000000000001

# True when a and b differ by no more than epsilon.
def within_epsilon(a, b, e=epsilon):
    return abs(a - b) <= e

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

# Object to collect pairs, then to look up an item's counterpart. Used here to
# associate instances of Flock and Visualizer (can't subclass: Open3D bug #572).
class Pairings:
    def __init__(self):
        self.dict = {}
    def add_pair(self, a, b):
        self.dict[a] = b
        self.dict[b] = a
    def get_peer(self, x):
        return self.dict[x]

# Utility for blending per-step values into accumulators for low pass filtering.
class Blender:
    def __init__(self, initial_value=None):
        self.value = initial_value
    # "smoothness" controls how much smoothing. Values around 0.8-0.9 seem most
    # useful. smoothness=1 is infinite smoothing. smoothness=0 is no smoothing.
    def blend(self, new_value, smoothness):
        self.value = (new_value if self.value == None
                      else interpolate(smoothness, new_value, self.value))
        return self.value

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
    p = Pairings()
    p.add_pair(1.23, 'a')
    p.add_pair('foo', (1,2))
    assert p.get_peer(1.23) == 'a'
    assert p.get_peer('a') == 1.23
    assert p.get_peer('foo') == (1,2)
    assert p.get_peer((1,2)) == 'foo'
    # TODO 20230409 test random-number utilities, later RandomSequence.
