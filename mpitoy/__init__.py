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
    def __init__(self, capacity=10, name=None):
        if not name:
            raise RuntimeError("Parameter 'name' is required.")
        self.name = name
        self.capacity = max(10,capacity)# maximum number of particles the container can accomodate without growing
        self.growthFactor = 1.2         #
        self.size = 0                   # actual number of particles
        self.arrays = {}                # dict of arrays in containeer
        self.defval = {}                # default value of each array
        self.addArray('alive',False)    # only particles for which alive[i]==True exist
        self.free = []                  # list of free elements. if empty the next free element is given by self.size

    def addArray(self, name: str, default_value=None):
        """Add an array to the particle container."""
        contents = [ copy(default_value) for i in range(self.capacity)]
        #   if default_value is mutable, we need copies, otherwise all elements
        #   in the array will refer to the same object. If not, the copy doesn't harm.
        setattr(self, name, contents)
        self.arrays[name] = getattr(self,name)
        self.defval[name] = default_value

    def resetElement(self, array_name, i):
        array = self.arrays[array_name]
        array[i] = copy(self.defval[array_name])
        #   if the default value is mutable, we need a copy, otherwise all elements
        #   in the array will refer to the same object. If not, the copy doesn't harm.

    def get_default_value(self, value, n=0):
        """if value is mutable, we need to copy value"""
        if n == 0:
            # return a single value
            if value in (int, float, bool, type(None),):
                return value
            else:
                return copy(value)
        else:
            # return a list of n values
            result = n*[value]
            if not value in (int, float, bool, type(None),):
                for i in range(n):
                    result[i] = copy(value)
            return result

    def removeArray(self,name):
        """remove an array from the particle container."""
        delattr(self,name)
        del self.arrays[name]
        del self.defval[name]

    def grow(self):
        """Increase capacity"""
        n = int(round( self.capacity * (self.growthFactor - 1), 0 ) )
        if n==0:
            n = self.capacity

        for name,array in self.arrays.items():
            array.extend([copy(self.defval[name]) for i in range(n)])
        self.capacity += n

    def remove(self, i, reset=False):
        """Remove particle i. If reset is True, reset the i-th element of all arrays to its default value."""
        if not self.alive[i]:
           raise RuntimeError(f"Particle {i} is already removed.")
        self.alive[i] = False
        self.free.append(i)
        self.size -= 1
        if reset:
            for name,array in self.arrays.items():
                array[i] = copy(self.defval[name])

    def addElement(self):
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

    def array2str(self, array_name, rnd=2, id=False):
        a = self.arrays[array_name]
        s = f'{self.name}.{array_name}[{"id" if id else ""}] =[ '
        for i in range(self.capacity):
            if self.alive[i]:
                s += f'{self.id[i] if id else i}={round(a[i],rnd)}, '
        s += ']'
        return s

    def clone(self, elements=[], move=False, verbose=False, name=None):
        """Clone this ParticleContainer. The clone will have exactythe same arrays.
        The array contents may differ: the elements in the elements list are copied
        or moved, depending on the value of move. You can select all element by
        setting elements='all'.
        """
        nm = f'{self.name}_clone' if not name else name
        cloned = ParticleContainer(name=nm)
        for name in self.arrays.keys():
            cloned.addArray(name,self.defval[name])
        for i in (range(self.capacity) if elements=='all' else elements):
            if self.alive[i]:
                j = cloned.addElement()
                # copy element j for all arrays
                for name, array in self.arrays.items():
                    cloned.arrays[name][j] = array[i]
                if move:
                    self.remove(i)
            else:
                if verbose:
                    print(f'clone() ignoring dead element ({i}).')
        return cloned



class Spheres(ParticleContainer):
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
    print(type(plt.cm.rainbow(np.linspace(0, 1, n))))
    COLORS = list(iter(plt.cm.rainbow(np.linspace(0, 1, n))))

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

