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

class Simulation:
    def __init__(self, n, xbound=None, label='None'):
        # using 2 dimensions, X,Y
        shape = (2,n)
        self.x = np.zeros(shape)
        self.v = np.zeros(shape)
        self.a = np.zeros(shape)
        self.radius = 0.5
        for i in range(n):
            self.x[0,i] = i + self.radius # X-coordinate
            self.v[0,i] = 0.1
        self.x[1,:] = self.radius        # y-coordinate
        self.t = 0
        self.dt = 1
        self.xbound = xbound
        self.label = label

    def move(self,nTimesteps=1):
        for i in range(nTimesteps):
            self.v += self.a * self.dt
            self.x += self.v * self.dt
            self.t += self.dt
        # print(f"Simuation.move: {self.t=}")


    @property
    def n(self):
        return self.x.shape[1]

    @property
    def diameter(self):
        return 2*self.radius

    def plot(self, show=False, save=False):
        n = self.n
        fig, ax = plt.subplots()
        ax.set_aspect(1.0)
        ax.set_xbound(*self.xbound)
        ax.set_ybound((0,self.diameter))


        color = iter(plt.cm.rainbow(np.linspace(0, 1, n)))
        for i in range(n):
            circle = plt.Circle(self.x[:,i], self.radius, color=next(color))
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
            self.circles[i].center = self.x[:, i]
        self.move(self.nTimestepsPerFrame)
        return []


    def movie(self,nTimesteps=10, nTimestepsPerFrame=1):
        self.nTimestepsPerFrame = nTimestepsPerFrame
        n = self.n

        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect(1.0)
        self.ax.set_xbound(0, 2 * n * self.diameter)
        self.ax.set_ybound((0, self.diameter))

        self.circles = []
        color = iter(plt.cm.rainbow(np.linspace(0, 1, n)))
        for i in range(n):
            circle = plt.Circle(self.x[:, i], self.radius, color=next(color))
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
