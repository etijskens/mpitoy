# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')

"""Tests for mpitoy package."""
import numpy as np

from mpitoy import *
from mpitoy.simulation import setColors, Simulation


n = 5
setColors(n)

import matplotlib.pyplot as plt
import pytest


def test_move():
    pc = Spheres(1)
    sim = Simulation(pc)
    rx0 = pc.rx[0]
    dt, nTimesteps = 0.1, 1
    rx0 += pc.vx[0] * dt
    sim.move(dt=dt, nTimesteps=nTimesteps)
    assert pc.rx[0] == rx0
    assert sim.t == dt*nTimesteps


def test_plot():
    n = 5
    pc = Spheres(n)
    sim = Simulation(pc, xbound=(0,10), label='test_plot')
    sim.plot()
    plt.show()


def test_plot_twice():
    n = 5
    pc = Spheres(n)
    sim = Simulation(pc, xbound=(0,10), label='test_plot')
    sim.plot(save=True)
    sim.move(dt=1)
    sim.plot(save=True)


def test_plot_show():
    n = 5
    pc = Spheres(n)
    sim = Simulation(pc, xbound=(0,10), label='test_plot_show')
    sim.plot(show=True)


def test_plot_show_save():
    n = 5
    pc = Spheres(n)
    sim = Simulation(pc, xbound=(0,10), label='test_plot_show_save')
    sim.plot(show=True, save=True)


def test_findLeavingParticles():
    n = 2
    spheres = Spheres(n)
    sim = Simulation(spheres, xbound=(0,2), label='test_plot_show_save')
    while spheres.rx[1] < 2.02:
        sim.move(dt = 0.2)
        print(f"t={round(sim.t,4)}, {spheres.rx=}")
        outleft,outright = sim.findLeavingParticles(spheres)
        if outright:
            assert 1 in outright
            print(f'{outright=}')
            assert spheres.alive[1]
            assert spheres.id[1] == 1
            print('before clone:', spheres.array2str('rx',id=True))
            spheres_out = spheres.clone(outright, move=True, name='spheres_out')
            print(' after clone:', spheres.array2str('rx',id=True))
            print(' after clone:', spheres_out.array2str('rx',id=True))
            assert not spheres.alive[1]
            assert spheres_out.id[0] == 1
            break



# def test_movie():
#     n = 5
#         pc = Spheres(n)
#     sim = Simulation(pc)
#     sim.movie(nTimesteps=50)

# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (otherwise all tests are normally run with pytest)
# Make sure that you run this code with the project directory as CWD, and
# that the source directory is on the path
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_plot_twice

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof