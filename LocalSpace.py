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

import numpy as np
from Vec3 import Vec3
import Utilities as util

class LocalSpace:
    """Local space (transformation) for a boid/agent."""

    # Initialize new instance.
    def __init__(self):
        self.set_state_ijkp(Vec3(1, 0, 0),
                            Vec3(0, 1, 0),
                            Vec3(0, 0, 1),
                            Vec3(0, 0, 0))

    # Set non-homogeneous 3x4 portion of transform: 3 basis and one position vec.
    # TODO 20230417 should this be replace with optional arguments on __init__()?
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
        epsilon = 0.00000000000001 # works on my laptop with Python 3.10
        return (util.within_epsilon(self.i.length_squared(), 1, epsilon) and
                util.within_epsilon(self.j.length_squared(), 1, epsilon) and
                util.within_epsilon(self.k.length_squared(), 1, epsilon) and
                util.within_epsilon(self.i.dot(self.j), 0, epsilon) and
                util.within_epsilon(self.j.dot(self.k), 0, epsilon) and
                util.within_epsilon(self.k.dot(self.i), 0, epsilon))

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
        self.i = util.random_unit_vector()
        self.j = util.random_unit_vector()
        self.k = self.i.cross(self.j).normalize()
        self.j = self.k.cross(self.i).normalize()
        # assert self.is_orthonormal()

    @staticmethod
    def unit_test():
        identity_asarray = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0],
                                     [0, 0, 1, 0],
                                     [0, 0, 0, 1]])
        test_ls = LocalSpace()
        test_ls.set_state_ijkp(test_i := Vec3(1, 2, 3).normalize(),
                               test_j := test_i.cross(Vec3(0, 0, 1)).normalize(),
                               test_i.cross(test_j).normalize(),
                               Vec3(5, 6, 7))
        assert np.array_equal(LocalSpace().asarray(), identity_asarray)
        assert LocalSpace().is_orthonormal(), 'initial value is orthonormal'
        assert test_ls.is_orthonormal(), 'handmade value is orthonormal'
