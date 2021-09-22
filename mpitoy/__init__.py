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


class Simulation:
    def __init__(self,n):
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

    def plot(self,fig=None,ax=None):
        n = self.n
        if fig is None:
            fig, ax = plt.subplots()
            ax.set_aspect(1.0)
            ax.set_xbound(0,2*n*self.diameter)
            ax.set_ybound((0,self.diameter))
            return fig,ax
        else:
            color = iter(plt.cm.rainbow(np.linspace(0, 1, n)))
            for i in range(n):
                circle = plt.Circle(self.x[:,i], self.radius, color=next(color))
                ax.add_patch(circle)


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
