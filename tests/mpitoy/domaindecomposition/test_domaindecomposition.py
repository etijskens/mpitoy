#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
"""Tests for sub-module mpitoy.domainboundary."""
import pytest
from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs
from mpitoy.simulation import setColors, Simulation
from mpitoy import Spheres

def test_plane():
    plane = BoundaryPlane([5., 0., 0.], [-1., 0., 0.])
    assert plane.distance([4, 0, 0]) > 0
    assert plane.distance([5, 0, 0]) == 0
    assert plane.distance([6, 0, 0]) < 0


def test_ParallelSlabs():
    boundaries = ParallelSlabs(points=[[1, 0, 0], [2, 0, 0]], n=[1, 0, 0])
    assert boundaries.size == 2


def test_findLeavingParticles():
    spheres = Spheres(2)
    bp = BoundaryPlane(p=[1,0,0],n=[1,0,0])
    outside = bp.findLeavingParticles(spheres)
    assert outside == [1]

def test_findGhostParticles():
    spheres = Spheres(5)
    bp = BoundaryPlane(p=[5,0,0],n=[1,0,0])
    toBeGhosted = bp.findGhostParticles(spheres,ghostWidth=01.0)
    assert toBeGhosted == [4]


if __name__ == "__main__":
    the_test_you_want_to_debug = test_findLeavingParticles
    the_test_you_want_to_debug()
    print("-*# finished #*-")
# ==============================================================================
