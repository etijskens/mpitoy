import sys
sys.path.insert(0,'.')

from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs, PcSendRecv
from mpitoy.simulation import setColors, Simulation
from mpitoy import Spheres
from mpitoy.mprint import mprint

from mpi4py import MPI
comm = MPI.COMM_WORLD

import pytest

mprint('imports finished')

@pytest.mark.mpi(min_size=2)
def test():
    """"""
    assert comm.rank <=6

    n = 5
    spheres = Spheres(n, id0=n * comm.rank)
    boundaryPoints = []
    x = 0
    for r in range(comm.size - 1):
        x += 5
        boundaryPoints.append([x, 0, 0])

    slabs = ParallelSlabs(points=boundaryPoints, n=[1, 0, 0])
    boundaries = slabs.decompose(comm)
    mprint(f'{[str(bp) for bp in boundaries]}')

    # every domain sends the element next to the boundary to its neighbour
    # there are 2 PcSendRreceive objects for every boundary (left->right and vv)
    pcsrs = []
    for ibp, bp in enumerate(boundaries):
        if bp.myRank < bp.nbRank:
            elements = [4]
        else:
            elements = [0]
        pcsr = PcSendRecv(spheres, bp, elements=elements)
        pcsrs.append(pcsr)

    for pcsr in pcsrs:
        pcsr(verbose=True)
        for array in pcsr.pc.arrays.values():
            if not array.name == 'alive':
                mprint(array)

if __name__ == "__main__":
    test()
    mprint('-*# finished #*-')