# -*- coding: utf-8 -*-

"""Tests for mpitoy package."""
import numpy as np

import mpitoy
import matplotlib.pyplot as plt


def test_init():
    n = 5
    sim = mpitoy.Simulation(n)
    for i in range(n):
        assert sim.x[0,i] == i
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
    sim = mpitoy.Simulation(n=5)
    fig,ax = sim.plot()
    sim.plot(fig,ax)
    plt.show()


def test_plot1():
    sim = mpitoy.Simulation(n=1)
    fig, ax = sim.plot()
    sim.plot(fig,ax)
    plt.show()

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
    the_test_you_want_to_debug = test_movie

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof