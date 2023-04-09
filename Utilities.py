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
    ok = True
    ok &= (clip01(1.5) == 1)
    ok &= (clip01(0.5) == 0.5)
    ok &= (clip01(-1) == 0)
    ok &= (clip(0, 1, 5) == 1)
    ok &= (clip(1.5, 1, 5) == 1.5)
    ok &= (clip(0, -1, -5) == -1)
    ok &= (between(0, 1, 2) == False)
    ok &= (between(1.5, 1, 2) == True)
    ok &= (between(1.5, 2, 1) == True)
    ok &= (between(0, -1, 1) == True)
    ok &= (between(-2, 1, -1) == False)
    ok &= (rehash32bits(2653567485) == 1574776808)
    
    # TODO 20230409 test random-number utilities, later RandomSequence.

    return ok

################################################################################


#    // Square a float
#    inline float sq(float f) { return f * f; }
#

#
#    // TODO 20230302 grabbed this from TexSyn, probably needs a lot of refitting.
#    // Simple self-contained generator for a sequence of psuedo-random 32 bit values
#    class RandomSequence
#    {
#    public:
#        // Constructor with default seed.
#        RandomSequence() : state_(defaultSeed()) {}
#        // Constructor with given seed.
#        RandomSequence(uint64_t seed) : state_(uint32_t(seed)) {}
#        // Next random number in sequence as a 31 bit positive int.
#        uint32_t nextInt() { return bitMask() & nextUint32(); }
#        // Next random number in sequence as a 32 bit unsigned int.
#        uint32_t nextUint32() { return state_ = rehash32bits(state_); }
#        // A 32 bit word with zero sign bit and all other 31 bits on, max pos int.
#        uint32_t bitMask() { return 0x7fffffff; } // 31 bits
#        // The largest (31 bit) positive integer that can be returned.
#        int maxIntValue() { return bitMask(); }
#        // A "large" 32 bit "random" number.
#        static uint32_t defaultSeed() { return 688395321; }
#
#        // TODO look at removing the old versions of these utilities.
#        // Returns a float randomly distributed between 0 and 1
#        float frandom01() { return float(nextInt()) / float(maxIntValue()); }
#        // Returns a float randomly distributed between lowerBound and upperBound
#        float frandom2(float a, float b) { return interpolate(frandom01(), a, b); }
#        // Returns an int randomly distributed between 0 and n-1.
#        int randomN(int n) { return nextInt() % n; }
#        int randomN(size_t n) { return nextInt() % n; }
#        // int/float overloads of random2(), returns value between INCLUSIVE bounds.
#        int random2(int i, int j) { assert(i<=j); return i + randomN(j - i + 1); }
#        float random2(float i, float j) { return frandom2(i, j); }
#        // Returns true or false with equal likelihood.
#        bool randomBool() { return random2(0, 1); }
#        // Return random element of given std::vector.
#        template<typename T> T randomSelectElement(const std::vector<T>& collection)
#        { return collection.at(randomN(collection.size())); }
#
#    //    // TODO these duplicate the function of the same name in global namespace.
#    //    //  Maybe those should be replaced by defining a global RandomSequence which
#    //    // must be specifically written in source code. This may help avoid the
#    //    // "attractive nuisance" of random utilities which are non-repeatable.
#    //    Vec2 randomPointInUnitDiameterCircle();
#    //    Vec2 randomUnitVector();
#    //    // Random point (position vector) in an axis aligned rectangle defined by
#    //    // two diagonally opposite vertices.
#    //    Vec2 randomPointInAxisAlignedRectangle(Vec2 a, Vec2 b);
#    //    // TODO moved from Color class to here on June 30, 2020:
#    //    Color randomUnitRGB();
#
#        Vec3 randomUnitVector();
#        Vec3 randomPointInUnitRadiusSphere();
#        Vec3 randomPointInAxisAlignedBox(Vec3 a, Vec3 b);
#
#        // Set seed (RS state) to given value, or defaultSeed() if none given.
#        void setSeed() { state_ = defaultSeed(); }
#        void setSeed(uint32_t seed) { state_ = seed; }
#        // Get state.
#        uint32_t getSeed() { return state_; }
#    private:
#        uint32_t state_;
#    };
