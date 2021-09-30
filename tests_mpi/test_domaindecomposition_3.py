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
def test():
    print("\ntest_DomainDecompositionParallel()")

    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    domain = ParallelSlabs([[1, 0, 0], [2, 0, 0]], n=[1, 0, 0])
    myBoundaries = domain.decompose(comm)
    for b in myBoundaries:
        b.prnt(comm)



if __name__ == "__main__":
    test()
    print("-*# finished #*-")
# ==============================================================================
