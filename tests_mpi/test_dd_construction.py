import sys

import pytest

sys.path.insert(0,'.')

from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs
from mpitoy.simulation import setColors, Simulation
from mpitoy import Spheres
from mpi4py import MPI

@pytest.mark.mpi(min_size=3)
def test():
    print("\ntest_simulation_with_domain_decomposition()")
    comm = MPI.COMM_WORLD
    slabs = ParallelSlabs([[5, 0, 0],[10,0,0]], n=[1, 0, 0])
    myBoundaries = slabs.decompose(comm)
    for b in myBoundaries:
        b.prnt(comm)
    domain = myBoundaries.constructDomain()
    d

    N = 5 # total number particles
    setColors(N) # every process needs the same colors

    n = N if comm.rank == 0 else 0 # number of particles in this rank.
    spheres = Spheres(n, name='spheres')

    xbound = (N*comm.rank, N*(comm.rank+1))
    ybound = (0,1)
    sim = Simulation(spheres, name=f"[{comm.rank=}]")
    sim.plot(xbound=xbound, ybound=ybound, save=True)

    ### start time evolution ###
    while sim.t < 6:
        sim.move(dt=0.4)
        print(f"\n{comm.rank=} {sim.t=}, {spheres.rx}")
        for bp in myBoundaries:
            leaving = bp.findLeavingParticles(spheres, comm=comm, verbose=True)
            if leaving:
                print(f"{comm.rank=} {bp}: {leaving=}, {sim.t=}")
                assert leaving == [4]
            ghost = bp.findGhostParticles(spheres, ghostWidth=1., comm=comm, verbose=True)
            if ghost:
                print(f"{comm.rank=} {bp}: {ghost=}, {sim.t=}")
                assert ghost == [4]
        sim.plot(xbound=xbound, ybound=ybound, save=True)
        print(f'{comm.rank=} ; Barrier')
        comm.Barrier()


if __name__ == "__main__":
    test()
    print("-*# finished #*-")