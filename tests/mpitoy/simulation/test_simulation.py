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
    sim = Simulation(pc, name='test_plot')
    sim.plot(xbound=(0,10), ybound=(0,1))
    plt.show()


def test_plot_twice():
    n = 5
    pc = Spheres(n)
    sim = Simulation(pc, name='test_plot')
    sim.plot(xbound=(0,10), ybound=(0,1), save=True)
    sim.move(dt=1)
    sim.plot(save=True)


def test_plot_show():
    n = 5
    pc = Spheres(n)
    sim = Simulation(pc, name='test_plot_show')
    sim.plot(xbound=(0,10), ybound=(0,1), show=True)


def test_plot_show_save():
    n = 5
    pc = Spheres(n)
    sim = Simulation(pc, name='test_plot_show_save')
    sim.plot(xbound=(0,10), ybound=(0,1), show=True, save=True)


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