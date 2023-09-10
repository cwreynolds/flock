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



    ############################################################################
    # TODO 20230815 experiment
    # version of sphere_avoidance without "if dist_squared < min_dist ** 2:"
    
#    def sphere_avoidance_EXPERIMENT(self, min_dist, radius, center):
#        avoidance = Vec3()
#        path_intersection = Vec3.ray_sphere_intersection(self.position,
#                                                         self.forward,
#                                                         radius, center)
#        if path_intersection:
#            # Near enough to require avoidance steering?
#            dist_squared = (path_intersection - self.position).length_squared()
#            if dist_squared < min_dist ** 2:
#                toward_center = center - path_intersection
#                pure_steering = toward_center.perpendicular_component(self.forward)
#                avoidance = pure_steering.normalize()
#                if self.flock.enable_annotation:
#                    c = Vec3(0.9, 0.7, 0.9) # magenta
#                    Draw.add_line_segment(self.position, path_intersection, c)
#        return avoidance
#
#    # TODO 20230815 experiment -- thinking about continuous version
#    def avoidance_strength(min_dist, intersection_dist):
#        falloff = 1 / (intersection_dist - min(intersection_dist, min_dist))
#        return 1 - falloff

    ############################################################################

