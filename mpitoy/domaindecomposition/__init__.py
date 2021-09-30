# -*- coding: utf-8 -*-

"""
Module mpitoy.domainboundary
==========================

A submodule for ...

"""

import numpy as np
from copy import copy

class TagComposer:
	"""Class TagComposer composes a unique int from a list of ints.

	"""
	def __init__(self, digits=[]):
		"""

		:param digits: list of number of digits per item in the list, specified from left to right
		 	digits[0] is not used.
		"""
		if not digits:
			raise ValueError("you must specify digits")
		if sum(digits) > 16:
			raise ValueError(f"sun(digits)={sum(digits)} cannot exceed 16.")
		self.digits = digits
		self.maxval = [10**d for d in digits]

	@property
	def n(self):
		return len(self.digits)


	def __call__(self, *args):
		"""Compose the tag from args.
		:param args: specified from left to right
		:return:
		"""
		tag = args[0]
		for i in range(1, self.n):
			if args[i] > self.maxval[i]:
				raise ValueError(f'{i}-th parameter (={args[i]}) exceeds maximum (={self.maxval[i]}')
			tag *= self.maxval[i]
			tag += args[i]
		return tag

	def decompose(self,tag):
		s = str(tag)+' '
		iend = -1
		args = []
		for i in range(self.n-1, -1, -1):
			if i == 0:
				si = s[:iend]
			else:
				si = s[iend - self.digits[i] : iend]
			args.insert(0, int(si))
			iend -= self.digits[i]
		return args


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

	The BoundaryPlane object stores the rank of the domain (self.myRank), and that of its neighbour
	on the other side of the domain (self.nbRank)::

		 boundary plane
			   | n
		nbRank |---> myrank
			   |


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
		self.myRank = None # the rank responsible for points inside the domain (positive location)
		self.nbRank = None # the rank responsible for points crossing this domain boundary (negative location)
		self.ghostPCs = {}
		self.tagger = TagComposer(digits=[2,2,3,3])

	def send_tag(self, pc_id, caller_id):
		"""Compose a tag from the sender and the receiver rank. If you send with tag=send_tag() you must
		receive with tag=recv_tag().

		:return: int
		:raises: TypeError if self.me or self.nb are None. (which means that there is no MPI context.
		"""
		tag = self.tagger(pc_id, caller_id, self.myRank, self.nbRank)
		print(tag)
		return tag

	def recv_tag(self, pc_id, caller_id):
		"""
		:return: int, a tag that is composed for
		:raises: TypeError if self.me or self.nb are None. (which means that there is no MPI context.
		"""
		tag = self.tagger(pc_id, caller_id, self.nbRank, self.myRank)
		print(tag)
		return tag


	def __str__(self):
		return f"{self.myRank}-|>{self.nbRank}"

	def prnt(self,comm):
		"""
		MPI communicator
		:param comm:
		:return:
		"""
		print(f"{comm.rank=}: p={self.p}, n={self.n}, me={self.myRank}, nb={self.nbRank}")

	def distance(self, q):
		"""Compute the signed distance of point q to this BoundaryPlane.
		A positive (negative) distance indicates that q is inside (outside) the domain.

		:param np.ndarray q: a point in space.
		:return: float.
		"""
		print(f'{self} {q-self.p}dot{self.n} = {np.dot(q-self.p,self.n)}')
		return np.dot(q-self.p,self.n)

	def findLeavingParticles(self, pc, comm=None, verbose=False):
		"""Find the particles in particle container pc that are outside the domain.

		if a communicator is provided, the particles in pc that cross this BoundaryPlane from are
		moved from to pc in the neighbouring domain, and vice versa. This involves MPI communication
		in both directions

		If a communicator is provided, this function must be called on all ranks.
		"""
		outgoing = []
		if verbose:
			print(f"findLeavingParticles({str(self)}) : pc initially contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
		for i in range(pc.capacity):
			if pc.alive[i]:
				pi = np.array([pc.rx[i],pc.ry[i],pc.rz[i]])
				di = self.distance(pi)
				if di < 0:
					outgoing.append(i)
					if verbose:
						print(f'findLeavingParticles({str(self)}) : outgoing.append({pc.id[i]=}), {pc.rx[i]=}, {di=}')
		if comm:
			if outgoing:
				# make a clone with the outgoing particles, moving them from the pc to its clone:
				pc_outgoing = pc.clone(elements=outgoing, move=True)
				if verbose:
					outgoing_elements = [pc.id[i] for i in outgoing]
					print(f"findLeavingParticles({str(self)}) : sending particles {outgoing_elements}")
			else:
				pc_outgoing = None
				if verbose:
					print(f"findLeavingParticles({str(self)}) : sending None")

			#send the clone to the neighbouring domain:
			req_outgoing = comm.isend(pc_outgoing, dest=self.nbRank, tag=self.send_tag(1,pc.ID))
			req_outgoing.wait()
			# Receive leaving particles from the neighbouring domain
			req_incoming = comm.irecv(source=self.nbRank, tag=self.recv_tag(1,pc.ID))
			pc_incoming = req_incoming.wait()
			if not pc_incoming is None:
				if verbose:
					incoming_elements = [pc_incoming.id[i] for i in range(pc_incoming.capacity) if pc_incoming.alive[i]]
					print(f"findLeavingParticles({str(self)}) rank{comm.rank} receiving particles {incoming_elements}")
				# Copy the incoming particles
				pc_incoming.copyto(pc)
				if verbose:
					print(f"findLeavingParticles({str(self)}) rank{comm.rank} pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
			else:
				if verbose:
					print(f"findLeavingParticles({str(self)}) rank{comm.rank} receiving None")

		return outgoing


	def findGhostParticles(self, pc, ghostWidth=None, comm=None, verbose=False):
		"""Find the particles in pc that need to be ghosted in the neighbouring domain.
		Returns a list of indexes of particles in pc for which the distance to this
		BoundaryPlane is in [ghostWidht,0].

		If a communicator is provided, the pc sends the ghost particles from this domain, to pc in the neighbouring
		domain and receives the leaving particles from pc in the neighbouring domain.

		If a communicator is provided, this function must be called on all ranks.

		It is assumed that all particles of pc are outside the domain of this BoundaryPlane.
		"""
		if verbose:
			print(f"findGhostParticles rank{comm.rank} pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
		if pc.size == 0:
			# If ParticleContainer pc is empty, there is no need to ask for ghost particles.
			if verbose:
				print(f"findGhostParticles {comm.rank}: pc '{pc.name}' is empty. Ghost particles not needed.")
			return []

		toBeGhosted = []
		for i in range(pc.capacity):
			if pc.alive[i]:
				pi = np.array([pc.rx[i],pc.ry[i],pc.rz[i]])
				di = self.distance(pi)
				if 0 <= di < ghostWidth:
					toBeGhosted.append(i)

		if comm:
			if toBeGhosted:
				# Copy the particles to be ghosted to a clone
				pc_toBeGhosted = pc.clone(elements=toBeGhosted)
				if verbose:
					toBeGhosted_elements = [pc.id[i] for i in toBeGhosted]
					print(f"findGhostParticles rank{comm.rank} sending ghost particles {toBeGhosted_elements}")
					print(f"findGhostParticles rank{comm.rank} pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
			else:
				pc_toBeGhosted = None

			#send the ghost clone to the neighbouring domain:
			req_toBeGhosted = comm.isend(pc_toBeGhosted, dest=self.nbRank, tag=self.send_tag(2, pc.ID))
			req_toBeGhosted.wait()
			# Receive the ghost clone from the neighbouring domain
			req_toBeGhosted = comm.irecv(source=self.nbRank, tag=self.recv_tag(2, pc.ID))
			pc_toBeGhosted = req_toBeGhosted.wait()
			# Store the Ghost PC:
			self.ghostPCs[pc.name] = pc_toBeGhosted
			if not pc_toBeGhosted is None:
				if verbose:
					toBeGhosted_elements = [pc_toBeGhosted.id[i] for i in range(pc_toBeGhosted.capacity) if pc_toBeGhosted.alive[i]]
					print(f"findGhostParticles rank{comm.rank} receiving ghost particles {toBeGhosted_elements}")

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
			b.myRank = rank
			b.nbRank = rank + 1
			b.n *= -1 # have normal point inward
			myBoundaryPlanes.append(b)

		elif rank == comm.size - 1:
			# Last domain, has only boundary with lower rank
			b = copy(self.boundaries[rank-1])
			b.myRank = rank
			b.nbRank = rank - 1
			myBoundaryPlanes.append(b)

		else:
			# Interior domains have two boundaries, with higher and lower rank
			# lower rank:
			b = copy(self.boundaries[rank-1])
			b.myRank = rank
			b.nbRank = rank - 1
			myBoundaryPlanes.append(b)
			# higher rank
			b = copy(self.boundaries[rank])
			b.myRank = rank
			b.nbRank = rank + 1
			b.n *= -1 # have normal point inward
			myBoundaryPlanes.append(b)

		return myBoundaryPlanes

	@property
	def size(self):
		return len(self.boundaries)
