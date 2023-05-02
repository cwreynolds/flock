#-------------------------------------------------------------------------------
#
# LocalSpace.h -- new flock experiments
#
# Local space (transformation) for a boid/agent.
#
# Equivalent to a 4x4 homogeneous transformation with [0 0 0 1] as last column:
#     [ ix iy iz 0 ]
#     [ jx jy jz 0 ]
#     [ kx ky kz 0 ]
#     [ px py pz 1 ]
# For rigid transformations (position, orientation) basis vectors i, j, and k
# are unit length and mutually perpendicular.
#
# MIT License -- Copyright © 2023 Craig Reynolds#
#-------------------------------------------------------------------------------

import copy
import numpy as np
from Vec3 import Vec3
import Utilities as util

class LocalSpace:
    """Local space (transformation) for a boid/agent."""

    # Initialize new instance.
    def __init__(self,
                 i=Vec3(1, 0, 0),
                 j=Vec3(0, 1, 0),
                 k=Vec3(0, 0, 1),
                 p=Vec3(0, 0, 0)):
        self.set_state_ijkp(i, j, k, p)

    # Set non-homogeneous 3x4 portion of transform: 3 basis and 1 position vec.
    def set_state_ijkp(self, i, j, k, p):
        # Basis vectors of local coordinate axes, ijk → xyz:
        self.i = i
        self.j = j
        self.k = k
        # Position of local center:
        self.p = p

    # 20230409 TODO this assumes unit length, orthonormal bases.
    #               Should either generalize (why?) or put in an assert.
    def localize(self, global_vector):
        v = global_vector - self.p
        return Vec3(v.dot(self.i),  v.dot(self.j), v.dot(self.k))

    def globalize(self, local_vector):
        v = local_vector
        return ((v.x * self.i) + (v.y * self.j) + (v.z * self.k) + self.p)

    def is_orthonormal(self):
        return (util.within_epsilon(self.i.length_squared(), 1) and
                util.within_epsilon(self.j.length_squared(), 1) and
                util.within_epsilon(self.k.length_squared(), 1) and
                util.within_epsilon(self.i.dot(self.j), 0) and
                util.within_epsilon(self.j.dot(self.k), 0) and
                util.within_epsilon(self.k.dot(self.i), 0))

    # TODO 20230405 speculative API, maybe for PinholeCameraParameters?
    def asarray(self):
        return np.array([[self.i.x, self.i.y, self.i.z, 0],
                         [self.j.x, self.j.y, self.j.z, 0],
                         [self.k.x, self.k.y, self.k.z, 0],
                         [self.p.x, self.p.y, self.p.z, 1]])

    # Describe LocalSpace as string.
    def __str__(self):
        return ("[i="  + str(self.i) +
                ", j=" + str(self.j) +
                ", k=" + str(self.k) +
                ", p=" + str(self.p) + "]")

    # Set to random orientation. Almost certainly the wrong way to do this.
    def randomize_orientation(self):
        self.i = Vec3.random_unit_vector()
        self.j = Vec3.random_unit_vector()
        self.k = self.i.cross(self.j).normalize()
        self.j = self.k.cross(self.i).normalize()
        return self

    @staticmethod
    def unit_test():
        identity_asarray = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0],
                                     [0, 0, 1, 0],
                                     [0, 0, 0, 1]])
        ls_i = Vec3(1, 2, 3).normalize()
        ls_j = ls_i.cross(Vec3(0, 0, 1)).normalize()
        ls_k = ls_i.cross(ls_j).normalize()
        ls_p = Vec3(5, 6, 7)
        ls = LocalSpace(ls_i, ls_j, ls_k, ls_p)
        r = copy.copy(ls).randomize_orientation()
        a = Vec3.random_point_in_unit_radius_sphere() * 10
        b = Vec3.random_point_in_unit_radius_sphere() * 100
        assert np.array_equal(LocalSpace().asarray(), identity_asarray)
        assert LocalSpace().is_orthonormal(), 'initial value is orthonormal'
        assert ls.is_orthonormal(), 'handmade ls is orthonormal'
        assert r.is_orthonormal(), 'randomized ls is still orthonormal'
        assert a.is_equal_within_epsilon(r.globalize(r.localize(a)))
        assert a.is_equal_within_epsilon(r.localize(r.globalize(a)))
        assert b.is_equal_within_epsilon(r.globalize(r.localize(b)))
        assert b.is_equal_within_epsilon(r.localize(r.globalize(b)))
        
        # Just to verify that copy.copy() works for LocalSpace, as expected.
        a = LocalSpace()
        b = copy.copy(a)
        a.i = Vec3(1, 2, 3)
        b.p = Vec3(9, 8, 7)
        assert b.i == Vec3(1, 0, 0), 'verify copy.copy() prevents sharing'
        assert a.p == Vec3(0, 0, 0), 'verify copy.copy() prevents sharing'
