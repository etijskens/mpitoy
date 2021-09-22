"""
run this script as::

    > mpirun -np <number of processes> python tests/dd3.py


check https://gist.github.com/shwina/64d2af01c563f9f74eea
"""
import sys
sys.path.insert(0,'.')

from mpi4py import MPI
import numpy as np

from mpitoy import Simulation, plt


size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

print(f"dd3.py: process {rank} of {size} on {name}.\n")

def main():
    """"""
    # Every process makes his own simulation
    if rank == 0:
        n = 5
    else:
        n = 0

    xbound = (5*rank,5*(rank+1))
    sim = Simulation(n, xbound=xbound, label=f"[{rank=}]")
    sim.plot(save=True)

    sendbuffer     = -np.ones((2,), dtype=float)
    recvbufferleft = -np.ones((2,), dtype=float)
    recvbufferrght = -np.ones((2,), dtype=float)

    sendbuffer[:] = xbound

    if 0 < rank < size-1:
        print(f'{rank=} sending to the left : {sendbuffer=}')
        MPI.COMM_WORLD.Send(sendbuffer, dest=rank-1)
        print(f'{rank=} sending to the right: {sendbuffer=}')
        MPI.COMM_WORLD.Send(sendbuffer, dest=rank+1)

    if rank != size-1:
        print(f'{rank=} receiving from the right')
        MPI.COMM_WORLD.Recv(recvbufferrght, source=rank+1)
    else: # last rank
        print(f'{rank=} sending to the left : {sendbuffer=}')
        MPI.COMM_WORLD.Send(sendbuffer, dest=rank-1)

    if rank != 0:
        print(f'{rank=} receiving from the left')
        MPI.COMM_WORLD.Recv(recvbufferleft, source=rank-1)
    else: # rank 0
        print(f'{rank=} sending to the right: {sendbuffer=}')
        MPI.COMM_WORLD.Send(sendbuffer, dest=rank+1)

    print(f'{rank=}:\n  {sendbuffer=}\n  {recvbufferleft=}\n  {recvbufferrght=}')
    print(f'{rank=} finished.')

if __name__ == "__main__":
    main()