#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
"""Tests for sub-module mpitoy.domainboundary."""
import pytest
from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs
from mpitoy import Spheres


@pytest.mark.mpi(min_size=2)
def test():
    print("\ntest_findLeavingParticles()")
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    domain = ParallelSlabs([[4, 0, 0], [8, 0, 0]], n=[1, 0, 0])
    myBoundaries = domain.decompose(comm)
    if comm.rank == 0:
        spheres = Spheres(5)
    else:
        spheres = Spheres(0)
    for bp in myBoundaries:
        bp.findLeavingParticles(spheres, comm=comm, verbose=True)
    if comm.rank == 0:
        assert spheres.size == 4
        for i in range(5):
            if i  == 4:
                assert not spheres.alive[i]
            else:
                assert spheres.alive[i]
    elif comm.rank == 1:
        assert spheres.size == 1
        assert not spheres.alive[4]

if __name__ == "__main__":
    test()
    print("-*# finished #*-")
# ==============================================================================
