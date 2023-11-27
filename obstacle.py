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
from Draw import Draw
#import Utilities as util

class Obstacle:
    def __init__(self):
        self.tri_mesh = None

    # Where the ray representing an Agent's path will intersect the obstacle.
    def ray_intersection(self, origin, tangent):
        pass

    # Normal to the obstacle at a given point of interest.
    def normal_at_poi(self, poi, agent_position=None):
        pass

    # Point on surface of obstacle nearest the given query_point
    def nearest_point(self, query_point):
        pass

    # Compute direction for agent's static avoidance of (concave?) obstacles.
    def fly_away(self, agent_position, agent_forward, max_distance):
        pass

    def draw(self):
        pass

    def __str__(self):
        return self.__class__.__name__

class EvertedSphereObstacle(Obstacle):
    def __init__(self, radius, center):
        Obstacle.__init__(self)
        self.radius = radius
        self.center = center

    # Where the ray representing an Agent's path will intersect the obstacle.
    def ray_intersection(self, origin, tangent):
        return Vec3.ray_sphere_intersection(origin, tangent,
                                            self.radius, self.center)

    # Normal to the obstacle at a given point of interest.
    def normal_at_poi(self, poi, agent_position=None):
        return (self.center - poi).normalize()

    # Point on surface of obstacle nearest the given query_point
    def nearest_point(self, query_point):
        return (query_point - self.center).normalize() * self.radius

    # Compute direction for agent's static avoidance of (concave?) obstacles.
    def fly_away(self, agent_position, agent_forward, max_distance):
        avoidance = Vec3()
        p = agent_position
        r = self.radius
        c = self.center
        offset_to_sphere_center = c - p
        distance_to_sphere_center = offset_to_sphere_center.length()
        dist_from_wall = r - distance_to_sphere_center
        # Close enough to obstacle surface to use static replusion.
        if dist_from_wall < max_distance:
            normal = offset_to_sphere_center / distance_to_sphere_center
            # Unless agent is already facing away from obstacle.
            if normal.dot(agent_forward) < 0.9:
                # Weighting falls off further from obstacle surface
                weight = 1 - (dist_from_wall / max_distance)
                avoidance = normal * weight
        return avoidance
    
    def draw(self):
        if not self.tri_mesh:
            self.tri_mesh = Draw.make_everted_sphere(self.radius, self.center)
        Draw.adjust_static_scene_object(self.tri_mesh)

class PlaneObstacle(Obstacle):
    def __init__(self, normal=Vec3(0, 1, 0), center=Vec3(0, 0, 0)):
        Obstacle.__init__(self)
        self.normal = normal
        self.center = center

    # Where the ray representing an Agent's path will intersect the obstacle.
    def ray_intersection(self, origin, tangent):
        return Vec3.ray_plane_intersection(origin, tangent,
                                           self.center, self.normal)

    # Normal to the obstacle at a given point of interest.
    def normal_at_poi(self, poi, agent_position=None):
        normal = self.normal
        # If a reference position is given.
        if agent_position:
            # Project it to obstacle surface.
            on_obstacle = self.nearest_point(agent_position)
            # Normalized vector FROM obstacle surface TOWARD agent.
            normal = (agent_position - on_obstacle).normalize()
        return normal

    # Point on surface of obstacle nearest the given query_point
    def nearest_point(self, query_point):
        # Offset from center point (origin) of plane.
        offset = query_point - self.center
        # Signed distance from plane.
        distance =  offset.dot(self.normal)
        # Translate offset point onto plane (in plane's local space).
        on_plane = offset - (self.normal * distance)
        # Translate back to global space.
        return on_plane + self.center

    # Compute direction for agent's static avoidance of (concave?) obstacles.
    def fly_away(self, agent_position, agent_forward, max_distance):
        avoidance = Vec3()
        # Project agent_position to obstacle surface.
        on_obstacle = self.nearest_point(agent_position)
        dist_from_obstacle = (on_obstacle - agent_position).length()
        # Close enough to obstacle surface to use static replusion.
        if dist_from_obstacle < max_distance:
            normal = self.normal_at_poi(on_obstacle, agent_position)
            # Unless agent is already facing away from obstacle.
            if normal.dot(agent_forward) < 0.9:
                # Weighting falls off further from obstacle surface
                weight = 1 - (dist_from_obstacle / max_distance)
                avoidance = normal * weight
        return avoidance

################################################################################
# TODO 20231122 WIP for CylinderObstacle: mock avoidance, endpoints ignored.
#
# for now lets ignore the endpoints and assume the cylinder is infinitely long.

# A bounded cylinder (between two endpoints) with given radius
class CylinderObstacle(Obstacle):
    def __init__(self, radius, endpoint0, endpoint1):
        Obstacle.__init__(self)
        self.radius = radius
        self.endpoint = endpoint0
        offset = endpoint1 - endpoint0
        self.length = offset.length()
        self.tangent = offset.normalize()

    # Nearest point on the infinite line containing cylinder's axis.
    def nearest_point_on_axis(self, query_point):
        offset = query_point - self.endpoint
        projection = offset.dot(self.tangent)
        return self.endpoint + self.tangent * projection

    ### “pure virtual methods” of Obstacle to specialize
    
    # Where the ray representing an Agent's path will intersect the obstacle.
    def ray_intersection(self, origin, tangent):
        ########################################################################
        # TODO 20231122 mock implementation
        return (self.nearest_point_on_axis(origin) +
                self.normal_at_poi(origin)  * self.radius)
        ########################################################################

    # Normal to the obstacle at a given point of interest.
    def normal_at_poi(self, poi, agent_position=None):
        on_axis = self.nearest_point_on_axis(poi)
        return (poi - on_axis).normalize()

    # Point on surface of obstacle nearest the given query_point
    def nearest_point(self, query_point):
        pass

    # Compute direction for agent's static avoidance of (concave?) obstacles.
    def fly_away(self, agent_position, agent_forward, max_distance):
        # does nothing for now?
        return Vec3()

    def draw(self):
        if not self.tri_mesh:
            self.tri_mesh = Draw.new_empty_tri_mesh()
            Draw.add_line_segment(self.endpoint,
                                  self.endpoint + (self.tangent * self.length),
                                  color = Vec3(1, 1, 1) * 0.98,
                                  radius = self.radius,
                                  sides = 10,
                                  tri_mesh = self.tri_mesh)
        Draw.adjust_static_scene_object(self.tri_mesh)

################################################################################

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
