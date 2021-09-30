# -*- coding: utf-8 -*-

"""
Module mpitoy.particlecontainer
==========================

A submodule for the ParticleContainer class
"""
from copy import copy


class ParticleArray(list):
    """Particle arrays behave as plain Python lists. In addition they store the

        * the name of the particle array,
        * a reference to the particle container to which the particle array belongs,
        * the default value of the particle array
    """
    def __init__(self, pc, name=None, defaultValue=None):
        if not name:
            raise RuntimeError("Parameter 'name' is required.")
        if name in pc.arrays:
            raise RuntimeError(f"Name '{name}' is already useed for another ParticleArray of ParticleContainer '{pc.name}'.")
        if hasattr(pc, name):
            raise RuntimeError(f"Name '{name}' is already used for an attribute of ParticleContainer '{pc.name}'.")
        self.name = name
        self.defaultValue = defaultValue
        self.pc = pc
        setattr(pc,name,self)   # make the array accessible as pc.name
        if name != 'alive':
            pc.arrays[name] = self  # make the array accessible as pc[name]
        # initialize the contents of the array.
        super().__init__()
        self.extend(pc.capacity*[copy(defaultValue)])
        #   if defaultValue is mutable, we need copies, otherwise all elements in
        #   the array will refer to the same object. If not, the copy doesn't harm.

    def reset(self,i='all'):
        """Reset a a single element (e.g i=3), all elements (i='all', =default),
        or a list of elements (i=[1,3]) to the array's default value.
        """
        if isinstance(i, list): # list of element indices
            for j in i:
                self.reset(j)
        elif i == 'all': # all elements (default)
            self = [ copy(self.defaultValue) for i in range(self.pc.capacity) ]
        else: # single element index
            self[i] = copy(self.defaultValue)

    def grow_(self,n):
        """Grow the array by n elements.

        This method is only to be used by ParticleContainer.grow()
        """
        self.extend(n*[copy(self.defaultValue)])

    def detach(self):
        """Detach this ParticleArray from its ParticleContainer.

        It will be garbage collected when it goes out of scope.
        """
        delattr(self.pc, self.name)
        del self.pc.arrays[self.name]
        self.pc = None

    def __str__(self):
        return f"{self.pc.name}.{self.name} = {list([self[i] for i in range(self.pc.capacity) if self.pc.alive[i]])}"


class ParticleContainer:
    """Base class for particle containers"""
    id = 0
    def __init__(self, capacity=10, name=None):
        if not name:
            raise RuntimeError("Parameter 'name' is required.")
        self.name = name
        self.capacity = max(10,capacity)# maximum number of particles the container can accomodate without growing
        self.growthFactor = 1.2         # if needed increase the capacity to growthFactor * capacity
        self.size = 0                   # actual number of particles
        self.arrays = {}                # dict of arrays in containeer
        ParticleArray(self, name='alive', defaultValue=False)
                                        # only particles for which alive[i]==True exist
        self.free = []                  # list of free elements. if empty the next free element is given by self.size
        ParticleContainer.id += 1
        self.id = ParticleContainer.id # used for tagging MPI messages

    def addArray(self, name: str, defaultValue=None): # deprecated, use ParticleArray.__init__() instead.
        """Add an array to the particle container."""
        ParticleArray(self, name=name, defaultValue=defaultValue)


    def removeArray(self,name):
        """remove an array from the particle container."""
        self.arrays[name].detach()

    def grow(self):
        """Increase capacity"""
        n = int(round( self.capacity * (self.growthFactor - 1), 0 ) )
        if n==0:
            n = self.capacity

        self.alive.grow_(n) # alive is not in self.arrays
        for array in self.arrays.values():
            array.grow_(n)
        self.capacity += n

    def kill(self, i, reset=False):
        """Remove particle i. If reset is True, reset the i-th element of all arrays to its default value.
        """
        if isinstance(i,list):
            for j in i:
                self.kill(j,reset)
        else:
            if not self.alive[i]:
               raise RuntimeError(f"Particle {i} is already removed.")
            self.alive[i] = False
            self.free.append(i)
            self.size -= 1
            if reset:
                for array in self.arrays.values():
                    array.reset(i)


    def addElement(self):
        """Add a particle and return its index.
        """
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

    # def array2str(self, array_name, rnd=2, id=False):
    #     """For pretty printing.
    #     """
    #     a = self.arrays[array_name]
    #     s = f'{self.name}.{array_name}[{"id" if id else ""}] =[ '
    #     for i in range(self.capacity):
    #         if self.alive[i]:
    #             s += f'{self.id[i] if id else i}={round(a[i],rnd)}, '
    #     s += ']'
    #     return s

    def clone(self, elements=[], move=False, verbose=False, name=None):
        """Clone this ParticleContainer. The clone will have exactly the same arrays.
        The array contents may differ: the elements in the elements list are copied
        or moved, depending on the value of move. You can select all element by
        setting elements='all'.
        """
        nm = f'{self.name}_clone' if not name else name
        cloned = ParticleContainer(name=nm)
        for array in self.arrays.values():

            ParticleArray(cloned, name=array.name, defaultValue=array.defaultValue)

        for i in (range(self.capacity) if elements=='all' else elements):
            if self.alive[i]:
                j = cloned.addElement()
                # copy element j for all arrays
                for name, array in self.arrays.items():
                    cloned.arrays[name][j] = array[i]
                if move:
                    self.kill(i)
            else:
                if verbose:
                    print(f'clone() ignoring dead element ({i}).')
        return cloned


    def copyto(self, pc):
        """copy all elements to pc"""
        for i in range(self.capacity):
            if self.alive[i]:
                j = pc.addElement()
                for name,array in self.arrays.items():
                    pc.arrays[name][j] = array[i]

