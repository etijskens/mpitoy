# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')


"""Tests for mpitoy package."""
import numpy as np

from mpitoy import *
import matplotlib.pyplot as plt
import pytest
setColors(5)

def test_PC_init():
    pc = ParticleContainer(name='pc')
    assert pc.capacity == 10
    assert pc.size == 0
    assert not pc.free
    assert 'alive' in pc.arrays
    assert pc.defval['alive'] == False
    for i in range(pc.capacity):
        assert pc.alive[i] == False

def test_PC_add_remove():
    pc = ParticleContainer(name='pc')
    with pytest.raises(RuntimeError):
        pc.remove(5)

    i = pc.addElement()
    assert i == 0
    assert pc.size == 1
    assert pc.alive[i] == True
    assert not pc.free

    i = pc.addElement()
    assert i == 1
    assert pc.size == 2
    assert pc.alive[i] == True
    assert not pc.free

    i = pc.addElement()
    assert i == 2
    assert pc.size == 3
    assert pc.alive[i] == True
    assert not pc.free

    pc.remove(1)
    assert pc.size == 2
    assert pc.alive[1] == False
    assert 1 in pc.free

    i = pc.addElement()
    assert i == 1
    assert pc.size == 3
    assert pc.alive[i] == True
    assert not pc.free

    for j in range(pc.capacity-pc.size):
        i = pc.addElement()
        assert pc.alive[i] == True
    assert pc.capacity == pc.size
    assert not pc.free

    i = pc.addElement()
    assert i == 10
    assert pc.size == 11
    assert pc.capacity == 12
    assert pc.alive[i] == True
    assert pc.alive[11] == False
    assert not pc.free

    pc.addArray('x',default_value=0)
    pc.x[i] = 10
    pc.remove(i,reset=True)
    assert pc.x[i] == 0

def test_PC_arrays():
    pc = ParticleContainer(name='pc')
    pc.addArray('x', default_value=0)
    for i in range(pc.capacity):
        assert pc.alive[i] == False
        assert pc.x[i] == 0
    pc.removeArray('x')
    with pytest.raises(AttributeError):
        print(pc.x[0])
    with pytest.raises(KeyError):
        pc.arrays['x']
    with pytest.raises(KeyError):
        pc.defval['x']


def test_spheres():
    n = 5
    pc = Spheres(n)
    assert pc.size == n
    radius = pc.radius[0]
    for i in range(n):
        assert pc.id[i] == i
        assert pc.rx[i] == (1+2*i)*radius
        assert pc.ry[i] == radius
        assert pc.vx[i] == 0.1
        assert pc.vy[i] == 0.0
        assert pc.ax[i] == 0.0
        assert pc.vy[i] == 0.0


def test_clone_empty():
    n = 5
    pc = Spheres(n)
    cloned = pc.clone()
    assert cloned.size == 0
    for name, array in pc.arrays.items():
        assert name in cloned.arrays
    for i in range(cloned.capacity):
        assert not cloned.alive[i]

def test_clone_23():
    n = 5
    pc = Spheres(n)
    elements_to_copy = [2,3]
    cloned = pc.clone(elements=elements_to_copy)
    assert cloned.size == len(elements_to_copy)
    for i in range(len(elements_to_copy)):
        j = elements_to_copy[i]
        assert cloned.id[i] == j
        assert cloned.vx[i] == pc.vx[j]

def test_clone_move23():
    n = 5
    pc = Spheres(n)
    elements_to_copy = [2,3]
    n_elements_to_copy = len(elements_to_copy)
    cloned = pc.clone(elements=elements_to_copy, move=True)

    assert pc.size == n - n_elements_to_copy
    for i in range(pc.capacity):
        if i in [0,1,4]:
            assert pc.alive[i]
            assert pc.id[i] == i
        else:
            assert not pc.alive[i]

    assert cloned.size == n_elements_to_copy
    for i in range(n_elements_to_copy):
        j = elements_to_copy[i]
        assert cloned.id[i] == j
        assert cloned.vx[i] == pc.vx[j]

def test_clone_all():
    n = 5
    pc = Spheres(n)
    elements_to_copy = 'all'
    cloned = pc.clone(elements=elements_to_copy)
    assert cloned.size == pc.size
    for i in range(pc.size):
        assert cloned.id[i] == i
        assert cloned.vx[i] == pc.vx[i]


def test_array2str():
    spheres = Spheres(5)
    spheres.id[3] = 2
    spheres.id[2] = 3

    s = spheres.array2str('rx')
    print(s)
    assert s == 'spheres.rx[] =[ 0=0.5, 1=1.5, 2=2.5, 3=3.5, 4=4.5, ]'

    s = spheres.array2str('rx', id=True)
    print(s)
    assert s == 'spheres.rx[id] =[ 0=0.5, 1=1.5, 3=2.5, 2=3.5, 4=4.5, ]'


if __name__ == "__main__":
    the_test_you_want_to_debug = test_array2str

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof