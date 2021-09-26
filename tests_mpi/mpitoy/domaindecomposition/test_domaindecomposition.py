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
def test_DomainDecompositionSimulation():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    domain = ParallelSlabs([[5, 0, 0], [10, 0, 0]], n=[1, 0, 0])
    myBoundaries = domain.decompose(comm)
    for b in myBoundaries:
        b.prnt(comm)

    N = 5 # total number particles
    n = N if comm.rank == 0 else 0 # number of particles in this rank.

    setColors(N) # every process needs the same colors

    spheres = Spheres(n)



if __name__ == "__main__":
    the_test_you_want_to_debug = test_DomainDecompositionSimulation

    the_test_you_want_to_debug()
    print("-*# finished #*-")
# ==============================================================================
