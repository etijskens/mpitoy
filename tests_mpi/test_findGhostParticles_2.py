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
    print("\ntest_findGhostParticles()")

    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    assert comm.size == 2

    domain = ParallelSlabs([[4, 0, 0]], n=[1, 0, 0])
    myBoundaries = domain.decompose(comm)
    spheres = Spheres(4)
    for i in range(4):
        spheres.rx[i] += comm.rank * 4
        spheres.id[i] += comm.rank * 4
    for bp in myBoundaries:
        bp.findGhostParticles(spheres, ghostWidth=1, comm=comm, verbose=True)

if __name__ == "__main__":
    test()
    print("-*# finished #*-")
# ==============================================================================
