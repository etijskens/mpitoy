# -*- coding: utf-8 -*-

"""
Package mpitoy
=======================================

Top-level package for mpitoy.
"""


__version__ = "0.2.0"

import mpitoy.mprint

import mpitoy.domaindecomposition

import mpitoy.simulation

import mpitoy.particlecontainer

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Spheres(mpitoy.particlecontainer.ParticleContainer):
    def __init__(self,n,name=None, id0=0):
        """

        :param n: number of particles to generate
        :param name: name of the particle container
        :param id0: number particle ids starting with id0. Allows to have distinct particle ids on different ranks.
        """
        nm = 'spheres' if name is None else name
        super().__init__(n,name=nm)
        radius = 0.5
        self.addArray('id', 0)
        self.addArray('radius', radius)
        self.addArray('rx')
        self.addArray('ry', radius)
        self.addArray('rz', radius)
        self.addArray('vx', 0.1)
        self.addArray('vy', 0.0)
        self.addArray('vz', 0.0)
        self.addArray('ay', 0.0)
        self.addArray('ax', 0.0)
        self.addArray('az', 0.0)
        for j in range(n):
            i = self.addElement()
            self.id[i] = id0 + i
            self.rx[i] = (1 + 2 * i) * radius

