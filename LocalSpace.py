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

class LocalSpace:
    """Local space (transformation) for a boid/agent."""

    # Initialize new instance.
    def __init__(self):
        self.set_state_ijkp(Vec3(1, 0, 0),
                            Vec3(0, 1, 0),
                            Vec3(0, 0, 1),
                            Vec3(0, 0, 0))
        self.__foobar = 0

    # Set non-homogeneous 3x4 portion of transform: 3 basis and one position vec.
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

    @staticmethod  # This decoration seems to be completely optional,
                   # but for the avoidance of doubt
    def unit_test():
        ok = True
        identity_asarray = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0],
                                     [0, 0, 1, 0],
                                     [0, 0, 0, 1]])
#        print('identity_asarray =', identity_asarray)
#        print('LocalSpace().asarray() =', LocalSpace().asarray())
        ok &= np.array_equal(LocalSpace().asarray(), identity_asarray)
        return ok
