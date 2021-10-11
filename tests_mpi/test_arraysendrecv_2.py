import sys
sys.path.insert(0,'.')

from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs, ArraySendRecv
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
    if comm.size == 2:

        n = 5
        spheres = Spheres(n, id0=n*comm.rank)
        boundaryPoints = []
        x = 0
        for r in range(comm.size-1):
            x += 5
            boundaryPoints.append([x,0,0])
        slabs = ParallelSlabs(points=boundaryPoints, n=[1,0,0])
        boundaries = slabs.decompose(comm)
        mprint(f'{[str(bp) for bp in boundaries]}')
        asrs = []
        # domain 0 sends element 0 to domain 1: this element has id==0
        # domain 1 sends element 4 to domain 0: this element has id==9
        elements = [[0],[4]]

        for ibp,bp in enumerate(boundaries):
            asr = ArraySendRecv(spheres.id, bp, elements=elements[comm.rank], verbose=True )
            asrs.append(asr)

        for asr in asrs:
            asr(verbose=True)
            if comm.rank == 0:
                assert 0 in asr.sendbuffer
                assert 9 in asr.recvbuffer
            elif comm.rank == 1:
                assert 9 in asr.sendbuffer
                assert 0 in asr.recvbuffer

    else:
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

        # domain i exchanges the i-th element with its right neighbour (i+1)
        # the id of the i-th element in domain i   is n*i     + i
        # the id of the i-th element in domain i+1 is n*(i+1) + i
        element = comm.rank

        asrs = []
        for ibp, bp in enumerate(boundaries):
            elements = [element] if bp.myRank < bp.nbRank else [element-1]
            mprint(f'{elements=}')
            asr = ArraySendRecv(spheres.id, bp, elements=elements)
            asrs.append(asr)

        for asr in asrs:
            asr(verbose=True)
            if asr.bp.myRank < asr.bp.nbRank:
                # sending right
                # receiving from left
                id0 = n* comm.rank    + comm.rank
                id1 = n*(comm.rank+1) + comm.rank
                mprint(asr.bp, id0,id1)
                assert id0 in asr.sendbuffer
                assert id1 in asr.recvbuffer
            else:
                # sending right to left
                # receiving from right
                id0 = n*(comm.rank-1) + comm.rank-1
                id1 = n* comm.rank    + comm.rank-1
                mprint(asr.bp, id0,id1)
                assert id0 in asr.recvbuffer
                assert id1 in asr.sendbuffer


if __name__ == "__main__":
    test()
    mprint('-*# finished #*-')