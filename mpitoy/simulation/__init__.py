# -*- coding: utf-8 -*-

"""
Module mpitoy.simulation
==========================

A submodule for ...

"""

import matplotlib.pyplot as plt
import numpy as np
from copy import copy


COLORS = None
def setColors(n):
    global COLORS
    COLORS = plt.cm.rainbow(np.linspace(0, 1, n))

def forward_euler(pc, dt=0.1, nTimesteps=1):
    for it in range(nTimesteps):
        for i in range(pc.capacity):
            if pc.alive[i]:
                pc.vx[i] += pc.ax[i]*dt
                pc.vy[i] += pc.ay[i]*dt
                pc.rx[i] += pc.vx[i]*dt
                pc.ry[i] += pc.vy[i]*dt

class Simulation:
    def __init__(self, pc, domainBoundaries=None, name=''):
        self.pcs = [pc]
        self.t = 0
        radius = pc.radius[0] # assuming all particles have the same radius
        self.domainBoundaries = domainBoundaries
        self.name = name


    def move(self,dt=0.1, nTimesteps=1):
        for pc in self.pcs:
            forward_euler(pc, dt=dt, nTimesteps=nTimesteps)
        self.t += nTimesteps*dt


    def plot(self, show=False, save=False, xbound=None, ybound=None):
        plt.close() # close previous figure if any.

        fig, ax = plt.subplots()
        ax.set_aspect(1.0)
        if xbound:
            ax.set_xbound(*xbound)
        if ybound:
            ax.set_ybound(*ybound)

        for pc in self.pcs:
            for i in range(pc.capacity):
                if pc.alive[i]:
                    id = pc.id[i]
                    circle = plt.Circle((pc.rx[i], pc.ry[i]), pc.radius[i], color=COLORS[id])
                    ax.add_patch(circle)
        title = copy(self.name)
        if title:
            title = self.name + ', '
        title += f't={round(self.t,2)}'
        plt.title(title)

        if show:
            plt.show()

        if save and self.name:
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


    # def findGhostParticles(self, xBound, ghostWidth):
    #     for i in range(self.capacity):
    #         if self.alive[i]:

