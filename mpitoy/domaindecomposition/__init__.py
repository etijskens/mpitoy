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

	def send_tag(self):
		"""Compose a tag from the sender and the receiver rank. If you send with tag=send_tag() you must
		receive with tag=recv_tag().

		:return: int
		:raises: TypeError if self.me or self.nb are None. (which means that there is no MPI context.
		"""
		return 1000*self.me + self.nb # this is readable for <= 1000 mpi processes.

	def recv_tag(self):
		"""
		:return: int, a tag that is composed for
		:raises: TypeError if self.me or self.nb are None. (which means that there is no MPI context.
		"""
		return 1000*self.nb + self.me # this is readable for <= 1000 mpi processes.

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

	def findLeavingParticles(self, pc, comm=None, verbose=False):
		"""Find the particles in particle container pc that are outside the domain.

		if a communicator is provided, the pc sends the leaving particles from this domain, to pc in the neighbouring
		domain and receives the leaving particles from pc in the neighbouring domain. If a communicator is provided,
		this function must be called on all ranks.
		"""
		outgoing = []
		if verbose:
			print(f"rank{comm.rank} pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
		for i in range(pc.capacity):
			if pc.alive[i]:
				pi = np.array([pc.rx[i],pc.ry[i],pc.rz[i]])
				di = self.distance(pi)
				if di < 0:
					outgoing.append(i)
		if comm:
			if outgoing:
				# move the leaving particles to a clone
				pc_outgoing = pc.clone(elements=outgoing, move=True)
				if verbose:
					outgoing_elements = [pc.id[i] for i in outgoing]
					print(f"rank{comm.rank} sending particles {outgoing_elements}")
					print(f"rank{comm.rank} pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
			else:
				pc_outgoing = None
			#send the clone to the neighbouring domain:
			req_outgoing = comm.isend(pc_outgoing, dest=self.nb, tag=self.send_tag())
			req_outgoing.wait()
			# Receive leaving particles from the neighbouring domain
			req_incoming = comm.irecv(source=self.nb, tag=self.recv_tag())
			pc_incoming = req_incoming.wait()
			if not pc_incoming is None:
				if verbose:
					incoming_elements = [pc_incoming.id[i] for i in range(pc_incoming.capacity) if pc_incoming.alive[i]]
					print(f"rank{comm.rank} receiving particles {incoming_elements}")
				pc_incoming.copyto(pc)
				if verbose:
					print(f"rank{comm.rank} pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")

		return outgoing


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
