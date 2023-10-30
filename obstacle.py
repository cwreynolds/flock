#-------------------------------------------------------------------------------
#
# obstacle.py -- new flock experiments
#
# Obstacle base class, some specializations, and utilities.
#
# An Obstacle is a type of geometry which Boids avoid.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------
# TODO 20230831 not sure this deserves its own file.
# TODO 20230831 I THINK I've read that Python modules ought to have lower case
#               names so now I have a mix, to be sorted out later.
# TODO 20230831 initiallly just a wrapper on the existing everted sphere, then
#               generalize that, add a cylinder type, maybe later a triangle
#               mesh type.
#-------------------------------------------------------------------------------

import math
from Vec3 import Vec3
#import Utilities as util

class Obstacle:
    def __init__(self):
        pass
    def ray_intersection(self, origin, tangent):
        pass
    def normal_at_poi(self, poi):
        pass

class EvertedSphereObstacle(Obstacle):
    def __init__(self, radius, center):
        self.radius = radius
        self.center = center
    def ray_intersection(self, origin, tangent):
        return Vec3.ray_sphere_intersection(origin,
                                            tangent,
                                            self.radius,
                                            self.center)
    def normal_at_poi(self, poi):
        return (self.center - poi).normalize()

    ############################################################################
    # TODO 20231030 WIP method to replace Boid.prototype_fly_away_from_obstacle
    def fly_away(self, position, forward, should_annotate):
        pass
    ############################################################################

class Collision:
    def __init__(self,
                 time_to_collision,
                 dist_to_collision,
                 point_of_impact,
                 normal_at_poi):
        self.time_to_collision = time_to_collision
        self.dist_to_collision = dist_to_collision
        self.point_of_impact = point_of_impact
        self.normal_at_poi = normal_at_poi
