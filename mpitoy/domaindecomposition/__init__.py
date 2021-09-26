# -*- coding: utf-8 -*-

"""
Module mpitoy.domainboundary
==========================

A submodule for ...

"""

import numpy as np
from copy import copy

class BoundaryPlane:
	"""Class for representing a boundary plane.

	The class stores a point on the plane (self.p), and the normal to the plane (self.n).

	The domain defined by the plane is the half space lying in the direction of the normal,
	i.e. the inside. The outside is the half space at the opposite side of the normal direction.
	The domain defined by a set of planes is the intersection of the insides of all the planes.

	The distance(q) method returns the **signed** distance of q to the plane:

	* if zero, q is on the plane
	* if > 0, q is inside the domain, i.e. in the half space lying in the direction of the normal.
	* if < 0  q is outside the domain, i.e. in the half space lying at the opposite direction of
	  the normal.
	"""
	def __init__(self, p, n=None):
		"""
		:param p: point p in the plane
		:param n: normal vector of the plane
		"""
		self.p = np.array(p)
		self.n = n / np.sqrt(np.dot(n, n)) # normalize

		# These are the ranks of the processes that correspond a positive location(), resp. a negative location()
		# These must be initiolized by the domain composition
		self.me = None # the rank responsible for points inside the domain (positive location)
		self.nb = None # the rank responsible for points crossing this domain boundary (negative location)

	def __str__(self):
		return f"p={self.p}, n={self.n}, me={self.me}, nb={self.nb}"

	def prnt(self,comm):
		"""
		MPI communicator
		:param comm:
		:return:
		"""
		print(f"{comm.rank=}: p={self.p}, n={self.n}, me={self.me}, nb={self.nb}")

	def distance(self, q):
		"""Locate position of point q relative to the plane.

		:param q: point to locate relative to the plane
		:return: float, if the result > 0, q is on the same side of the plane as the normal vector. If
			the result < 0, q is on the other side as the normal vector. if the result == 0, q is on
			the plane.
		"""
		return np.dot(q-self.p,self.n)

	def findLeavingParticles(self, pc):
		"""Find the particles that are outside the domain."""
		outside = []
		for i in range(pc.capacity):
			if pc.alive[i]:
				pi = np.array([pc.rx[i],pc.ry[i],pc.rz[i]])
				di = self.distance(pi)
				if di > 0:
					outside.append(i)
		return outside


	def findGhostParticles(self, pc, ghostWidth=None):
		"""Find the particles that need to be ghosted. Returns a list of indexes of particles in pc
		for which the distance to this BoundaryPlane is in [-ghostWidht,0].

		It is assumed that all particles of pc are outside the domain of this BoundaryPlane.
		"""
		signedGhostWidth = -ghostWidth if ghostWidth > 0 else ghostWidth
		toBeGhosted = []
		for i in range(pc.capacity):
			if pc.alive[i]:
				pi = np.array([pc.rx[i],pc.ry[i],pc.rz[i]])
				di = self.distance(pi)
				if di >= signedGhostWidth:
					if di > 0:
						raise RuntimeError(f'Particle {pc.name}.[{i}] is inside domain ({self.me}).')
					toBeGhosted.append(i)
		return toBeGhosted

class ParallelSlabs:
	""""""
	def __init__(self,points,n):
		"""
		:param points: list of successive points located on the respective boundary planes.
		:param n: normal vector of all planes.

		Currently, it is expected that the points are ordered correctly, i.e. the dot product of
		point[i]-point[0] with n should be increasing with i. It might be useful to enforce the
		ordering.
		"""
		boundaries = []
		dot = []
		for i,p in enumerate(points):
			points[i] = np.array(p)
		for p in points:
			plane = BoundaryPlane(p, n)
			boundaries.append(plane)
			dot.append(np.dot(p-points[0],n))
		dot_sorted = sorted(dot)
		if dot_sorted != dot:
			raise RuntimeError(f"Points must be sorted: {points}.")
		self.boundaries = boundaries


	def decompose(self,comm):
		"""Return a list of BoundaryPlanes for the current rank. The normals of the
		BoundaryPlanes are such that they define a slab for the current rank.

		for n+1 ranks we have:

		rank 0 | rank 1 | rank 2 |  ...  | rank n
		      BP0      BP1      BP2	   BPn-1

		If there are more BoundaryPlanes than ranks, they are not used.
		If there are too little, you get IndexError.
		"""
		myBoundaryPlanes = []
		if comm.size <= 0:
			return myBoundaryPlanes

		rank = comm.rank
		if rank == 0:
			# Domain 0, has only boundary with higher rank
			b = copy(self.boundaries[rank])
			b.me = rank
			b.nb = rank+1
			b.n *= -1 # have normal point inward
			myBoundaryPlanes.append(b)

		elif rank == comm.size - 1:
			# Last domain, has only boundary with lower rank
			b = copy(self.boundaries[rank-1])
			b.me = rank
			b.nb = rank-1
			myBoundaryPlanes.append(b)

		else:
			# Interior domains have two boundaries, with higher and lower rank
			# lower rank:
			b = copy(self.boundaries[rank-1])
			b.me = rank
			b.nb = rank-1
			myBoundaryPlanes.append(b)
			# higher rank
			b = copy(self.boundaries[rank])
			b.me = rank
			b.nb = rank+1
			b.n *= -1 # have normal point inward
			myBoundaryPlanes.append(b)

		return myBoundaryPlanes

	@property
	def size(self):
		return len(self.boundaries)
