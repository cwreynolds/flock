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

