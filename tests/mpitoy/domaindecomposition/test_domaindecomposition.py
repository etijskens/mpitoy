#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
"""Tests for sub-module mpitoy.domainboundary."""
import pytest
from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs

def test_plane():
    plane = BoundaryPlane([5., 0., 0.], [-1., 0., 0.])
    assert plane.distance([4, 0, 0]) > 0
    assert plane.distance([5, 0, 0]) == 0
    assert plane.distance([6, 0, 0]) < 0


def test_ParallelBoundaries():
    boundaries = ParallelSlabs([[1, 0, 0], [2, 0, 0]], [1, 0, 0])
    assert boundaries.size == 2

@pytest.mark.mpi(min_size=3)
def test_DomainDecompositionParallel():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    domain = ParallelSlabs([[1, 0, 0], [2, 0, 0]], n=[1, 0, 0])
    myBoundaries = domain.decompose(comm)
    for b in myBoundaries:
        b.prnt(comm)

if __name__ == "__main__":
    the_test_you_want_to_debug = test_ParallelBoundaries

    the_test_you_want_to_debug()
    print("-*# finished #*-")
# ==============================================================================
