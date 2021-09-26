#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
"""Tests for sub-module mpitoy.domainboundary."""
import pytest
from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs
from mpitoy.simulation import setColors, Simulation
from mpitoy import Spheres

@pytest.mark.mpi(min_size=3)
def test_DomainDecompositionParallel():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    domain = ParallelSlabs([[1, 0, 0], [2, 0, 0]], n=[1, 0, 0])
    myBoundaries = domain.decompose(comm)
    for b in myBoundaries:
        b.prnt(comm)

@pytest.mark.mpi(min_size=3)
def test_simulation_with_domain_decomposition():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    domain = ParallelSlabs([[5, 0, 0], [10, 0, 0]], n=[1, 0, 0])
    myBoundaries = domain.decompose(comm)
    for b in myBoundaries:
        b.prnt(comm)

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
        for bp in myBoundaries:
            leaving = bp.findLeavingParticles(spheres, comm=comm, verbose=True)
            if leaving:
                print(f"{comm.rank=}: {leaving=}, {sim.t=}")
                assert leaving == [4]
        sim.plot(xbound=xbound, ybound=ybound, save=True)


if __name__ == "__main__":
    the_test_you_want_to_debug = test_simulation_with_domain_decomposition

    the_test_you_want_to_debug()
    print("-*# finished #*-")
# ==============================================================================
