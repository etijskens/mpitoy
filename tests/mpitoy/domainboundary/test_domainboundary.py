#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for sub-module mpitoy.domainboundary."""
import numpy as np
import pytest
from mpitoy.domainboundary import Plane, ParallelBoundaries
from copy import copy

def test_plane():
    plane = Plane([5.,0.,0.], [-1.,0.,0.])
    assert plane.locate([4, 0, 0]) >  0
    assert plane.locate([5, 0, 0]) == 0
    assert plane.locate([6, 0, 0]) <  0


def test_ParallelBoundaries():
    boundaries = ParallelBoundaries([[1,0,0], [2,0,0]], [1,0,0])
    assert boundaries.size == 2

@pytest.mark.mpi(min_size=3)
def test_DomainDecompositionParallel():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    domain = ParallelBoundaries( [[1,0,0], [2,0,0]], n=[1,0,0] )
    myBoundaries = domain.decompose(comm)
    for b in myBoundaries:
        b.prnt(comm)

if __name__ == "__main__":
    the_test_you_want_to_debug = test_ParallelBoundaries

    the_test_you_want_to_debug()
    print("-*# finished #*-")
# ==============================================================================
