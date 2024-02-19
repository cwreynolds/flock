#------------------------------------------------------------------------------
#
# Utilities.py -- new flock experiments
#
# Utility functions
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#------------------------------------------------------------------------------

import time
import math
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

# This value (aka 1e-14) works on my laptop with Python 3.10 and c++17
epsilon = 0.00000000000001

# True when a and b differ by no more than epsilon.
def within_epsilon(a, b, e=epsilon):
    return abs(a - b) <= e

# Taken from https://en.wikipedia.org/wiki/Logistic_function
def logistic(x, k, L, x0):
    # Gets "OverflowError: math range error" for large negative values (eg -1000)
    x = max(x, -50)
    return L / (1 + math.exp(-k * (x - x0)))

# Logistic sigmoid (s-curve) from ~(0,0) to ~(1,1), ~0 if x<0, ~1 if x>1
# (See a plot of this function via Wolfram|Alpha: https://bit.ly/3sUYbeJ)
def unit_sigmoid_on_01(x):
    return logistic(x, 12, 1, 0.5)

# Remap a value specified relative to a pair of bounding values
# to the corresponding value relative to another pair of bounds.
# Inspired by (dyna:remap-interval y y0 y1 z0 z1) circa 1984.
# (20220108 borrowed from TexSyn's c++ Utilities package)
# (20230910 borrowed from PredatorEye's DiskFind.py)
# TODO -- note similar API in numpy
def remap_interval(x, in0, in1, out0, out1):
    # Remap if input range is nonzero, otherwise blend them evenly.
    input_range = in1 - in0
    blend = 0.5 if input_range == 0 else ((x - in0) / input_range)
    return interpolate(blend, out0, out1)

# Like remapInterval but the result is clipped to remain between out0 and out1
# (20220108 borrowed from TexSyn's c++ Utilities package)
# (20230910 borrowed from PredatorEye's DiskFind.py)
def remap_interval_clip(x, in0, in1, out0, out1):
    return clip(remap_interval(x, in0, in1, out0, out1), out0, out1)

# Are a and b on opposite sides of 0? Specifically: if they are the previous and
# current value of a "signed distance function" is/was there a zero crossing?
def zero_crossing(a, b):
    return ((a >= 0) and (b <= 0)) or ((a <= 0) and (b >= 0))

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

# Measure the execution time of a given "work load" function (of no arguments)
# and an optional suggested repetition count.
def executions_per_second(work_load, count=2000):
    start = time.perf_counter()
    for i in range(count):
        work_load()
    elapsed_seconds = time.perf_counter() - start
    
    executions_per_second = count / elapsed_seconds
    seconds_per_execution = 1 / executions_per_second
    print('seconds_per_execution =', seconds_per_execution)
    print('executions_per_second =', executions_per_second)
    return executions_per_second


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
        
    assert unit_sigmoid_on_01(0.5) == 0.5
    assert within_epsilon(unit_sigmoid_on_01(-1000), 0)
    assert within_epsilon(unit_sigmoid_on_01(+1000), 1)

    assert remap_interval(1.5, 1, 2, 20, 30) == 25
    assert remap_interval(1.5, 2, 1, 30, 20) == 25
    assert remap_interval(2, 1, 4, 10, 40) == 20
    assert remap_interval_clip(5, 1, 4, 10, 40) == 40
    assert remap_interval(1.5, 1, 2, 30, 20) == 25
    assert remap_interval(2, 1, 3, 30, 10) == 20
    assert remap_interval_clip(5, 1, 4, 40, 10) == 10
    assert not math.isnan(remap_interval(1, 1, 1, 2, 3))
    assert not math.isnan(remap_interval_clip(1, 1, 1, 2, 3))

    p = Pairings()
    p.add_pair(1.23, 'a')
    p.add_pair('foo', (1,2))
    assert p.get_peer(1.23) == 'a'
    assert p.get_peer('a') == 1.23
    assert p.get_peer('foo') == (1,2)
    assert p.get_peer((1,2)) == 'foo'

    b = Blender()
    assert b.value == None
    b.blend(1.2, 'ignored')
    assert b.value == 1.2
    b.blend(3.4, 0.9)
    assert b.value == 1.42
    b.blend(5.6, 0.5)
    assert b.value == 3.51
    
    # TODO 20230409 test random-number utilities, later RandomSequence.
