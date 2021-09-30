#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
"""Tests for sub-module mpitoy.domainboundary."""
import pytest
from mpitoy.domaindecomposition import BoundaryPlane, ParallelSlabs, TagComposer
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
    bp = BoundaryPlane(p=[1,0,0],n=[-1,0,0])
    outside = bp.findLeavingParticles(spheres)
    assert outside == [1]

def test_findGhostParticles():
    spheres = Spheres(5)
    bp = BoundaryPlane(p=[5,0,0],n=[1,0,0])
    toBeGhosted = bp.findGhostParticles(spheres,ghostWidth=01.0)
    assert toBeGhosted == [4]

def test_tagcomposer():
    tagger = TagComposer(digits=[2,2,2,2])

    args = [1,2,3,4]
    tag = tagger(*args)
    expected = 1020304
    assert tag == expected
    decomposed = tagger.decompose(tag)
    assert decomposed == args

    args = [10,20,30,40]
    tag = tagger(*args)
    expected = 10203040
    assert tag == expected
    decomposed = tagger.decompose(tag)
    assert decomposed == args

    args = [100,20,30,40]
    tag = tagger(*args)
    expected = 100203040
    assert tag == expected
    decomposed = tagger.decompose(tag)
    assert decomposed == args

    with pytest.raises(ValueError):
        tag = tagger(100, 200, 30, 40)


if __name__ == "__main__":
    the_test_you_want_to_debug = test_tagcomposer
    the_test_you_want_to_debug()
    print("-*# finished #*-")
# ==============================================================================
