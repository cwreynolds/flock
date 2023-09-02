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

from Vec3 import Vec3
#from Boid import Boid
#from Agent import Agent # do we need this?
#from flock import Flock
import Utilities as util
import math

class Obstacle:
    def __init__(self):
        pass
    def ray_intersection(origin, tangent):
        pass

class EvertedSphereObstacle(Obstacle):

    # TODO 20230901 very preliminary hard codes all the parameters that should
    #               be passed in
    def __init__(self, radius, center):
        self.radius = radius
        self.center = center
    def ray_intersection(origin, tangent):
        return Vec3.ray_sphere_intersection(origin,
                                            tangent,
                                            self.radius,
                                            self.center)

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
