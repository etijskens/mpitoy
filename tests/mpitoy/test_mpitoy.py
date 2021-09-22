# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')


"""Tests for mpitoy package."""
import numpy as np

from mpitoy import Simulation, ParticleContainer, setColors
import matplotlib.pyplot as plt

setColors(5)

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
    x0 += pc.v[0,:] * sim.dt
    sim.move(nTimesteps=1)
    for i in range(n):
        assert pc.x[0,i] == x0[i]
    assert sim.t == 1


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
    the_test_you_want_to_debug = test_movie

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof