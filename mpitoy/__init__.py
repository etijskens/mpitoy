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
    def __init__(self, capacity=10):
        self.capacity = max(10,capacity)# maximum number of particles the container can accomodate without growing
        self.growthFactor = 1.2         #
        self.size = 0                   # actual number of particles
        self.arrays = {}                # dict of arrays in containeer
        self.defval = {}                # default value of each array
        self.addArray('alive',False)    # only particles for which alive[i]==True exist
        self.free = []                  # list of free elements. if empty the next free element is given by self.size

    def addArray(self, name: str, default_value=None):
        """Add an array to the particle container."""
        setattr(self, name, self.capacity*[default_value])
        self.arrays[name] = getattr(self,name)
        self.defval[name] = default_value

    def grow(self):
        """Increase capacity"""
        n = int(round( self.capacity * (self.growthFactor - 1), 0 ) )
        if n==0:
            n = self.capacity

        for name,array in self.arrays.items():
            array.extend(n*[self.defval[name]])
        self.capacity += n

    def remove(self,i):
        """Remove particle i"""
        if not self.alive[i]:
           raise RuntimeError(f"Particle {i} is already removed.")
        self.alive[i] = False
        self.free.append(i)
        self.size -= 1

    def add(self):
        """Add a particle and return its index"""
        if self.size == self.capacity:
            self.grow()
        if not self.free:
            # list of free elements is empty,
            i = self.size
        else:
            i = self.free.pop()
        self.alive[i] = True
        self.size += 1
        return i

        #
        # self.radius = radius
        # # using 2 dimensions, X,Y
        # shape = (2,n)
        # self.x = np.zeros(shape)
        # self.v = np.zeros(shape)
        # self.a = np.zeros(shape)
        # self.id = np.zeros((n,), dtype=int)
        # for i in range(n):
        #     self.x[0,i] = i + radius # X-coordinate
        #     self.v[0,i] = 0.1
        #     self.id[i]  = i
        #
        # self.x[1,:] = radius         # y-coordinate
        #



    # def move(self, dt, nTimesteps):
    #     for i in range(nTimesteps):
    #         self.v += self.a * dt
    #         self.x += self.v * dt
    #

    # def findLeavingParticles(self,xbound):
    #     # we only check the X-boudaries
    #     movingOutLeft = []
    #     movingOutRght = []
    #
    #     for i in range(self.n):
    #         if self.x[0,i] < xbound[0]:
    #             movingOutLeft.append(i)
    #         if xbound[1] <= self.x[0,i]:
    #             movingOutRght.append(i)
    #     return movingOutLeft, movingOutRght


    # def remove(self, i):
    #     """remove particle i"""
    #     if not hasattr(self, 'alive'):
    #         self.alive = np.ones((self.n,),dtype=bool)

COLORS = None
def setColors(n):
    global COLORS
    print(type(plt.cm.rainbow(np.linspace(0, 1, n))))
    COLORS = list(iter(plt.cm.rainbow(np.linspace(0, 1, n))))

class Simulation:
    def __init__(self, pc=None, xbound=None, label=''):
        if pc is None:
            self.pc = ParticleContainer(0)
        else:
            self.pc = pc
        self.pcs = [pc]
        # using 2 dimensions, X,Y
        self.t = 0
        if xbound:
            self.xbound = xbound
        else:
            self.xbound = (0, pc.n*2*pc.radius)
        self.ybound = (0,2*pc.radius)
        self.label = label

    def move(self,dt=0.1, nTimesteps=1):
        for pc in self.pcs:
            pc.move(dt=dt, nTimesteps=nTimesteps)
        self.t += nTimesteps*dt


    def plot(self, show=False, save=False):
        plt.close()
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
        title += f't={round(self.t,2)}'
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
