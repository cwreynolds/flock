#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
# temp.py -- random experiments, prototype code
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import math
import Utilities as util
from Vec3 import Vec3
from LocalSpace import LocalSpace
from Agent import Agent

# TODO 20230827 logistic function

# Taken from https://en.wikipedia.org/wiki/Logistic_function
def logistic(x, k, L, x0):
    return L / (1 + math.exp(-k * (x - x0)))

def unit_sigmoid(x):
    return logistic(x / 10, 10, 1, 0)

def unit_sigmoid_on_01(x):
#    return logistic((x - 10) / 10, 10, 1, 0) + 0.5
#    return logistic((x - 10) / 10, 10, 1, 0) + 1
#    return logistic((x - 10) / 10, 10, 1, 0) + 0.5
#    return logistic((x + 10) / 10, 10, 1, 0)
    w = 12
#    return logistic(x / (w * 2), w, 1, 0.5)
    return logistic(x, w, 1, 0.5)


if __name__ == "__main__":
#        hr = 10
#        for i in range(-hr, hr+1):
#    #        print(i, logistic(i, 1, 1, 0))
#    #        print(i, logistic(i / 10, 10, 1, 0))
#    #        print(i, unit_sigmoid(i))
#            print(i, unit_sigmoid_on_01(i))
    for i in range(0, 101):
        x = i / 100
        print(x, unit_sigmoid_on_01(x))
