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

from Vec3 import Vec3

class LocalSpace:
    """Local space (transformation) for a boid/agent."""

    # Initialize new instance.
    def __init__(self):
        # Basis vectors of local coordinate axes, ijk → xyz:
        self.i = Vec3(1, 0, 0)
        self.j = Vec3(0, 1, 0)
        self.k = Vec3(0, 0, 1)
        # Position of local center:
        self.p = Vec3(0, 0, 0)

    # Describe LocalSpace as string.
    def __str__(self):
        return ("[i="  + str(self.i) +
                ", j=" + str(self.j) +
                ", k=" + str(self.k) +
                ", p=" + str(self.p) + "]")
