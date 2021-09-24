# -*- coding: utf-8 -*-

"""
Package mpitoy
=======================================

Top-level package for mpitoy.
"""


__version__ = "0.0.0"

import mpitoy.particlecontainer

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Spheres(mpitoy.particlecontainer.ParticleContainer):
    def __init__(self,n,name=None):
        nm = 'spheres' if name is None else name
        super().__init__(n,name=nm)
        radius = 0.5
        self.addArray('id', 0)
        self.addArray('radius', radius)
        self.addArray('rx')
        self.addArray('ry', radius)
        self.addArray('vx', 0.1)
        self.addArray('vy', 0.0)
        self.addArray('ay', 0.0)
        self.addArray('ax', 0.0)
        for j in range(n):
            i = self.addElement()
            self.id[i] = i
            self.rx[i] = (1 + 2 * i) * radius


def forward_euler(pc, dt=0.1, nTimesteps=1):
    for it in range(nTimesteps):
        for i in range(pc.capacity):
            if pc.alive[i]:
                pc.vx[i] += pc.ax[i]*dt
                pc.vy[i] += pc.ay[i]*dt
                pc.rx[i] += pc.vx[i]*dt
                pc.ry[i] += pc.vy[i]*dt

COLORS = None
def setColors(n):
    global COLORS
    COLORS = plt.cm.rainbow(np.linspace(0, 1, n))

class Simulation:
    def __init__(self, pc, xbound=None, label=''):
        self.pcs = [pc]
        self.t = 0
        radius = pc.radius[0] # assuming all particles have the same radius
        if xbound:
            self.xbound = xbound
        else:
            self.xbound = (0, pc.size * 2*radius)
        self.ybound = (0,2*radius)
        self.label = label


    def move(self,dt=0.1, nTimesteps=1):
        for pc in self.pcs:
            forward_euler(pc, dt=dt, nTimesteps=nTimesteps)
        self.t += nTimesteps*dt


    def plot(self, show=False, save=False):
        plt.close() # close previous figure if any.

        fig, ax = plt.subplots()
        ax.set_aspect(1.0)
        ax.set_xbound(*self.xbound)
        ax.set_ybound(*self.ybound)

        for pc in self.pcs:
            for i in range(pc.capacity):
                if pc.alive[i]:
                    id = pc.id[i]
                    circle = plt.Circle((pc.rx[i], pc.ry[i]), pc.radius[i], color=COLORS[id])
                    ax.add_patch(circle)
        title = copy(self.label)
        if title:
            title = self.label + ', '
        title += f't={round(self.t,2)}'
        plt.title(title)

        if show:
            plt.show()

        if save and self.label:
            print(f'Saving figure to {title}.png.')
            plt.savefig(title+'.png')


    # def movie_init(self):
    #     return []
    #
    #
    # def movie_update(self,frame):
    #     print(f'Simulation.movie_update {frame=}, t={self.t}')
    #     for i in range(self.n):
    #         self.circles[i].center = self.pc.x[:, i]
    #     self.move(self.nTimestepsPerFrame)
    #     return []
    #
    #
    # def movie(self,nTimesteps=10, nTimestepsPerFrame=1):
    #     self.nTimestepsPerFrame = nTimestepsPerFrame
    #
    #     self.fig, self.ax = plt.subplots()
    #     self.ax.set_aspect(1.0)
    #     self.ax.set_xbound(*self.xbound)
    #     self.ax.set_ybound(*self.ybound)
    #
    #     self.circles = []
    #     for pc in self.pcs:
    #         for i in range(pc.n):
    #             circle = plt.Circle(pc.x[:, i], pc.radius, color=COLORS[pc.id[i]])
    #             self.ax.add_patch(circle)
    #             self.circles.append(circle)
    #
    #     print(f"Simulation.movie:{nTimesteps=}")
    #     self.animation = FuncAnimation( self.fig
    #         , self.movie_update
    #         , frames=nTimesteps
    #         , init_func=self.movie_init
    #         , blit=True
    #         , repeat=False
    #         )
    #     plt.show()

    def findLeavingParticles(self, pc):
        movingOutLeft = []
        movingOutright= []
        for i in range(pc.capacity):
            if pc.alive[i]:
                # we check only the X-direction
                if pc.rx[i] < self.xbound[0]:
                    movingOutLeft.append(i)
                elif self.xbound[1] <= pc.rx[i]:
                    movingOutright.append(i)
        return movingOutLeft, movingOutright

    # def findGhostParticles(self, xBound, ghostWidth):
    #     for i in range(self.capacity):
    #         if self.alive[i]:

