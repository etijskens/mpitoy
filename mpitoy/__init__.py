# -*- coding: utf-8 -*-

"""
Package mpitoy
=======================================

Top-level package for mpitoy.
"""


__version__ = "0.0.0"

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from copy import copy

class ParticleContainer:
    def __init__(self,n,radius=.5):
        self.radius = radius
        # using 2 dimensions, X,Y
        shape = (2,n)
        self.x = np.zeros(shape)
        self.v = np.zeros(shape)
        self.a = np.zeros(shape)
        self.id = np.zeros((n,), dtype=int)
        for i in range(n):
            self.x[0,i] = i + radius # X-coordinate
            self.v[0,i] = 0.1
            self.id[i]  = i

        self.x[1,:] = radius         # y-coordinate


    @property
    def n(self):
        return self.id.shape[0]


    def move(self, dt, nTimesteps):
        for i in range(nTimesteps):
            self.v += self.a * dt
            self.x += self.v * dt

COLORS = None
def setColors(n):
    global COLORS
    print(type(plt.cm.rainbow(np.linspace(0, 1, n))))
    COLORS = list(iter(plt.cm.rainbow(np.linspace(0, 1, n))))

class Simulation:
    def __init__(self, pc=None, xbound=None, label='None', dt=1):
        if pc is None:
            self.pc = ParticleContainer(0)
        else:
            self.pc = pc
        self.pcs = [pc]
        # using 2 dimensions, X,Y
        self.t = 0
        self.dt = dt
        if xbound:
            self.xbound = xbound
        else:
            self.xbound = (0, pc.n*2*pc.radius)
        self.ybound = (0,2*pc.radius)
        self.label = label

    def move(self,nTimesteps):
        for pc in self.pcs:
            pc.move(dt=self.dt, nTimesteps=nTimesteps)
        self.t += nTimesteps*self.dt


    def plot(self, show=False, save=False):
        fig, ax = plt.subplots()
        ax.set_aspect(1.0)
        ax.set_xbound(*self.xbound)
        ax.set_ybound(*self.ybound)
        for pc in self.pcs:
            for i in range(pc.n):
                id = pc.id[i]
                circle = plt.Circle(pc.x[:,i], pc.radius, color=COLORS[id])
                ax.add_patch(circle)

        title = copy(self.label)
        if title:
            title = self.label + ', '
        title += f't={self.t}'
        plt.title(title)

        if show:
            plt.show()

        if save and self.label:
            print(f'Saving figure to {title}.png.')
            plt.savefig(title+'.png')


    def movie_init(self):
        return []


    def movie_update(self,frame):
        print(f'Simulation.movie_update {frame=}, t={self.t}')
        for i in range(self.n):
            self.circles[i].center = self.pc.x[:, i]
        self.move(self.nTimestepsPerFrame)
        return []


    def movie(self,nTimesteps=10, nTimestepsPerFrame=1):
        self.nTimestepsPerFrame = nTimestepsPerFrame

        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect(1.0)
        self.ax.set_xbound(*self.xbound)
        self.ax.set_ybound(*self.ybound)

        self.circles = []
        for pc in self.pcs:
            for i in range(pc.n):
                circle = plt.Circle(pc.x[:, i], pc.radius, color=COLORS[pc.id[i]])
                self.ax.add_patch(circle)
                self.circles.append(circle)

        print(f"Simulation.movie:{nTimesteps=}")
        self.animation = FuncAnimation( self.fig
            , self.movie_update
            , frames=nTimesteps
            , init_func=self.movie_init
            , blit=True
            , repeat=False
            )
        plt.show()


# class DomainDecomposition:
#     """Domain Decomposition: decmpose the space in slabs perpendicular to the X-axis"""
#     def __init__(self, xrange=(0,10),nDomains=2):
