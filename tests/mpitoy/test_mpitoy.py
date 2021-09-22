# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')
"""Tests for mpitoy package."""
import numpy as np

import mpitoy
import matplotlib.pyplot as plt


def test_init():
    n = 5
    sim = mpitoy.Simulation(n)
    for i in range(n):
        assert sim.x[0,i] == i+sim.radius
    assert sim.n == n


def test_move():
    n = 5
    sim = mpitoy.Simulation(n)
    x0 = np.copy(sim.x[0,:])
    x0 += sim.v[0,:] * sim.dt
    sim.move()
    for i in range(n):
        assert sim.x[0,i] == x0[i]
    assert sim.t == 1


def test_plot():
    sim = mpitoy.Simulation(n=5, xbound=(0,10), label='test_plot')
    sim.plot()
    plt.show()


def test_plot_show():
    sim = mpitoy.Simulation(n=5, xbound=(0,10), label='test_plot_show')
    sim.plot(show=True)


def test_plot_show_save():
    sim = mpitoy.Simulation(n=5, xbound=(0,10), label='test_plot_show_save')
    sim.plot(show=True, save=True)


def test_movie():
    sim = mpitoy.Simulation(n=5)
    sim.movie(nTimesteps=50)

# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (otherwise all tests are normally run with pytest)
# Make sure that you run this code with the project directory as CWD, and
# that the source directory is on the path
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_plot_show_save

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof