# -*- coding: utf-8 -*-

"""
Module mpitoy.domainboundary
==========================

A submodule for ...

"""

import numpy as np
from copy import copy
from mpitoy.mprint import mprint


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

    def send_tag(self, pc_id, caller_id, msg=''):
        """Compose a tag from the sender and the receiver rank. If you send with tag=send_tag() you must
        receive with tag=recv_tag().

        :return: int
        :raises: TypeError if self.me or self.nb are None. (which means that there is no MPI context.
        """
        tag = self.tagger(pc_id, caller_id, self.myRank, self.nbRank)
        if msg:
            print(f'{msg} send_tag:{tag}')
        return tag

    def recv_tag(self, pc_id, caller_id, msg=''):
        """
        :return: int, a tag that is composed for
        :raises: TypeError if self.me or self.nb are None. (which means that there is no MPI context.
        """
        tag = self.tagger(pc_id, caller_id, self.nbRank, self.myRank)
        if msg:
            print(f'{msg} recv_tag:{tag}')
        return tag


    def __str__(self):
        return f"{self.myRank}-|>{self.nbRank}"

    def prnt(self,comm):
        """
        MPI communicator
        :param comm:
        :return:
        """
        print(f"{comm.rank}: p={self.p}, n={self.n}, me={self.myRank}, nb={self.nbRank}")

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
            print(f"{comm.rank} findLeavingParticles({str(self)}) : pc initially contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
        for i in range(pc.capacity):
            if pc.alive[i]:
                pi = np.array([pc.rx[i],pc.ry[i],pc.rz[i]])
                di = self.distance(pi)
                if di < 0:
                    outgoing.append(i)
                    if verbose:
                        print(f'{comm.rank} findLeavingParticles({str(self)}) : outgoing.append({pc.id[i]=}), {pc.rx[i]=}, {di=}')
        if comm:
            if outgoing:
                # make a clone with the outgoing particles, moving them from the pc to its clone:
                pc_outgoing = pc.clone(elements=outgoing, move=True)
                if verbose:
                    outgoing_elements = [pc.id[i] for i in outgoing]
                    print(f"{comm.rank} findLeavingParticles({str(self)}) : sending particles {outgoing_elements}")
            else:
                pc_outgoing = None
                if verbose:
                    print(f"{comm.rank} findLeavingParticles({str(self)}) : sending None")

            #send the clone to the neighbouring domain:
            req_outgoing = comm.isend(pc_outgoing, dest=self.nbRank, tag=self.send_tag(1, pc.ID, msg=f'{comm.rank} findLeavingParticles'))
            req_outgoing.wait()
            # Receive leaving particles from the neighbouring domain
            req_incoming = comm.irecv(source=self.nbRank, tag=self.recv_tag(1, pc.ID, msg=f'{comm.rank} findLeavingParticles'))
            pc_incoming = req_incoming.wait()
            if not pc_incoming is None:
                if verbose:
                    incoming_elements = [pc_incoming.id[i] for i in range(pc_incoming.capacity) if pc_incoming.alive[i]]
                    print(f"{comm.rank} findLeavingParticles({str(self)}) receiving particles {incoming_elements}")
                # Copy the incoming particles
                pc_incoming.copyto(pc)
                if verbose:
                    print(f"{comm.rank} findLeavingParticles({str(self)}) pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
            else:
                if verbose:
                    print(f"{comm.rank} findLeavingParticles({str(self)}) receiving None")

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
            print(f"{comm.rank} findGhostParticles pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
        if pc.size == 0:
            # If ParticleContainer pc is empty, there is no need to ask for ghost particles.
            if verbose:
                print(f"{comm.rank} findGhostParticles: pc '{pc.name}' is empty. Ghost particles not needed.")

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
                    print(f"{comm.rank} findGhostParticles sending ghost particles {toBeGhosted_elements}")
                    print(f"{comm.rank} findGhostParticles pc contains {[pc.id[i] for i in range(pc.capacity) if pc.alive[i]]}")
            else:
                pc_toBeGhosted = None

            #send the ghost clone to the neighbouring domain:
            req_toBeGhosted = comm.isend(pc_toBeGhosted, dest=self.nbRank, tag=self.send_tag(2, pc.ID, msg=f'{comm.rank} findGhostParticles'))
            req_toBeGhosted.wait()
            #  req_outgoing = comm.isend(pc_outgoing   , dest=self.nbRank, tag=self.send_tag(1, pc.ID, msg=f'{comm.rank} findLeavingParticles'))
            # req_outgoing.wait()

            # Receive the ghost clone from the neighbouring domain
            req_toBeGhosted = comm.irecv(source=self.nbRank, tag=self.recv_tag(2, pc.ID, msg=f'{comm.rank} findGhostParticles'))
            pc_toBeGhosted = req_toBeGhosted.wait()
            # req_incoming  = comm.irecv(source=self.nbRank, tag=self.recv_tag(1, pc.ID, msg=f'{comm.rank} findLeavingParticles'))
            # pc_incoming = req_incoming.wait()
            # Store the Ghost PC:
            self.ghostPCs[pc.name] = pc_toBeGhosted
            if not pc_toBeGhosted is None:
                if verbose:
                    toBeGhosted_elements = [pc_toBeGhosted.id[i] for i in range(pc_toBeGhosted.capacity) if pc_toBeGhosted.alive[i]]
                    print(f"{comm.rank} findGhostParticles, receiving ghost particles {toBeGhosted_elements}")

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

        for b in myBoundaryPlanes:
            b.comm = comm

        return myBoundaryPlanes

    def constructDomain(self, comm, particleContainers):
        """Construct a Domain object.

        :param comm: a communicator, usually MPI.COMM_WORLD
        :return: a Domain object
        """
        boundaryPlanes = self.decompose(comm)
        domain = Domain(boundaryPlanes=boundaryPlanes, particleContainers=particleContainers)

    @property
    def size(self):
        return len(self.boundaries)

class TagStore:
    def __init__(self):
        self.last_tag = -1

    def getTag(self, n=1):
        """get n tags that have not been used before.

        Tags are successive, e.g. if getTag(3) returns 5, you can use the tags 3, 4 and 5.
        """
        self.last_tag += n
        return self.last_tag


tagStore = TagStore()

class ArraySendRecv:
    """
    Send/receive array elements to/from a neighbour.

    Set up point-to-point communication between the two domains on both sides of a boundary plane.
    An object of this class must be set up in both domains. Each object both sends and receives.
    E.g. domain i sends a message to domain i+1 and domain i+1 receives this message. Similarly,
    domoin i+1 sends a message to doain i and domain i receives this message. Both messages
    correspond to the same array, instantiated in both domains.

    Each domain needs as many Arraycommunicator objects as it has boundary planes.
    It is unclear whether the definition of a neighbourhood communicator would be important.
    let's studuy a bit
    """
    def __init__(self, array, bp, elements=[], verbose=False):
        self.array = array
        self.bp = bp
        self.elements_send = elements # the indices of the elements that must be sent

        # self.dtype = type(self.array.dtype)
        self.sendbuffer = []
        self.recvbuffer = []
        if self.bp.nbRank > self.bp.myRank:
            # send tag
            self.sendtag = tagStore.getTag(n=2)
            self.recvtag = self.sendtag - 1
            if verbose:
                mprint(bp, 'send tag ...')
            bp.comm.send(self.sendtag, bp.nbRank)
            if verbose:
                mprint(bp, f'send tag finished: {self.sendtag=}, {self.recvtag=}')
        else:
            # receive tag
            if verbose:
                mprint(bp, 'recv tag ...')
            self.recvtag = bp.comm.recv(source=self.bp.nbRank)
            self.sendtag = self.recvtag - 1
            if verbose:
                mprint(bp, f'recv tag finished: {self.sendtag=}, {self.recvtag=}')

        self.parent = None

    def __call__(self, verbose=False):
        # write the sendbuffer
        self.sendbuffer = []
        for ie in self.elements_send:
            self.sendbuffer.append(self.array[ie])

        reqsend = self.bp.comm.isend(self.sendbuffer, dest=self.bp.nbRank, tag=self.sendtag)
        reqsend.wait()
        reqrecv = self.bp.comm.irecv(source=self.bp.nbRank, tag=self.recvtag)
        self.recvbuffer = reqrecv.wait()
        if verbose:
            mprint(f'{self.bp}; {self.array.name}, {self.sendbuffer=}, {self.recvbuffer=}')

        if self.recvbuffer:
            # not empty
            # copy the contents of the recvbuffer to the array
            if self.parent and self.parent.elements_recv:
                elements_recv = self.parent.elements_recv
                if not len(elements_recv) == len(self.sendbuffer):
                    raise RuntimeError(f"recvbuffer for array '{self.array.py}.{self.array.name}'")
            else:
                # find locations for the new elements
                elements_recv = []
                pc = self.array.pc
                for val in self.recvbuffer:
                    i = pc.addElement()
                    elements_recv.append(i)

                # If this object has a parent (because several arrays of the particle container were communicated),
                # store the particle positions, so that subseauent arrays are using the same element location, as
                # expected.
                if self.parent:
                    self.parent.elements_recv = elements_recv
                # else: only a single array was sent.

            # mprint(f'{self.array}')
            for i, element in enumerate(elements_recv):
                # mprint(f'{i=}, {element=}, {self.array.name}, {self.array[element]}, {self.recvbuffer[i]}')
                self.array[element] = self.recvbuffer[i]
            mprint(f'{self.array}')

class PcSendRecv:
    """
    Send/receive PC elements to/from a neighbour.

    Set up point-to-point communication between the two domains on both sides of a boundary plane.
    An object of this class must be set up in both domains. Each object both sends and receives.
    E.g. domain i sends a message to domain i+1 and domain i+1 receives this message. Similarly,
    domoin i+1 sends a message to doain i and domain i receives this message. Both messages
    correspond to the same array, instantiated in both domains.

    Each domain needs as many Arraycommunicator objects as it has boundary planes.
    It is unclear whether the definition of a neighbourhood communicator would be important.
    let's studuy a bit
    """
    def __init__(self, pc, bp, elements=[], verbose=False):
        self.pc = pc
        self.bp = bp
        self.elements_send = elements # the indices of the elements that must be sent
        self.elements_recv = []
        self.asrs = []
        for array in pc.arrays.values():
            asr = ArraySendRecv(array, bp, elements=elements, verbose=verbose )
            asr.parent = self
            self.asrs.append(asr)


    def __call__(self, verbose=False):
        for asr in self.asrs:
            asr(verbose=verbose)


class Domain:
    """
    Domain objects are responsible for communication between neighbours
    """
    def __init__(self, boundaryPlanes, particleContainers):
        self.boundaryPlanes = boundaryPlanes
        self.particleContainers = particleContainers

        self.communications = []
        for pc in particleContainers:
            # attach an empty ghostParticleContainer
            pc.ghostParticles = pc.clone(name='ghostParticles')

            for array in pc.arrays.values():
                for bp in self.boundaryPlanes:
                    asr = ArraySendRecv(bp,array)
                    self.communications.append(sender)
                    recver = ArrayReceiver(bp,array)
                    self.communications.append(recver)


