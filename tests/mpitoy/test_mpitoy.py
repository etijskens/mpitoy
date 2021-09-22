# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')


"""Tests for mpitoy package."""
import numpy as np

from mpitoy import Simulation, ParticleContainer, setColors
import matplotlib.pyplot as plt
import pytest
setColors(5)

def test_PC_init():
    pc = ParticleContainer()
    assert pc.capacity == 10
    assert pc.size == 0
    assert not pc.free
    assert 'alive' in pc.arrays
    assert pc.defval['alive'] == Fals
    for i in range(pc.capacity):
        assert pc.alive[i] == False

def test_PC_add_remove():
    pc = ParticleContainer()
    with pytest.raises(RuntimeError):
        pc.remove(5)

    i = pc.add()
    assert i == 0
    assert pc.size == 1
    assert pc.alive[i] == True
    assert not pc.free

    i = pc.add()
    assert i == 1
    assert pc.size == 2
    assert pc.alive[i] == True
    assert not pc.free

    i = pc.add()
    assert i == 2
    assert pc.size == 3
    assert pc.alive[i] == True
    assert not pc.free

    pc.remove(1)
    assert pc.size == 2
    assert pc.alive[1] == False
    assert 1 in pc.free

    i = pc.add()
    assert i == 1
    assert pc.size == 3
    assert pc.alive[i] == True
    assert not pc.free

    for j in range(pc.capacity-pc.size):
        i = pc.add()
        assert pc.alive[i] == True
    assert pc.capacity == pc.size
    assert not pc.free

    i = pc.add()
    assert i == 10
    assert pc.size == 11
    assert pc.capacity == 12
    assert pc.alive[i] == True
    assert pc.alive[11] == False
    assert not pc.free


def test_PC_arrays():
    pc = ParticleContainer()
    pc.addArray('x', default_value=0)
    for i in range(pc.capacity):
        assert pc.alive[i] == False
        assert pc.x[i] == 0

def test_init():
    n = 5
    pc = ParticleContainer(n)
    sim = Simulation(pc)
    for i in range(n):
        assert pc.x[0,i] == i + pc.radius
    assert pc.n == n


def test_move():
    n = 5
    pc = ParticleContainer(n)
    sim = Simulation(pc)
    x0 = np.copy(pc.x[0,:])
    dt, nTimesteps = 0.1, 1
    x0 += pc.v[0,:] * dt
    sim.move(dt=dt, nTimesteps=nTimesteps)
    for i in range(n):
        assert pc.x[0,i] == x0[i]
    assert sim.t == dt*nTimesteps


def test_plot():
    n = 5
    pc = ParticleContainer(n)
    sim = Simulation(pc, xbound=(0,10), label='test_plot')
    sim.plot()
    plt.show()


def test_plot_show():
    n = 5
    pc = ParticleContainer(n)
    sim = Simulation(pc, xbound=(0,10), label='test_plot_show')
    sim.plot(show=True)


def test_plot_show_save():
    n = 5
    pc = ParticleContainer(n)
    sim = Simulation(pc, xbound=(0,10), label='test_plot_show_save')
    sim.plot(show=True, save=True)


# def test_movie():
#     n = 5
#     pc = ParticleContainer(n)
#     sim = Simulation(pc)
#     sim.movie(nTimesteps=50)

# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (otherwise all tests are normally run with pytest)
# Make sure that you run this code with the project directory as CWD, and
# that the source directory is on the path
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_PC_arrays

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof