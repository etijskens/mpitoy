# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')

"""Tests for mpitoy package."""

from mpitoy.particlecontainer import ParticleContainer,ParticleArray
from mpitoy import Spheres

import pytest

@pytest.mark.mpi(min_size=2)
def test_size():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    print(comm.size)
    assert comm.size >= 2

@pytest.mark.mpi(min_size=2)
def tests_send_pc():
    """
    Can we send and receive a ParticleContainer object?
    :return:
    """
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    print(f'{rank=}')
    if rank == 0:
        # spheres = Spheres(5, name='spheres')
        data = {'a': 7, 'b': 3.14}
        req = comm.isend(data, dest=1, tag=11)
        req.wait()

        data = None
        req = comm.isend(data, dest=1, tag=12)
        req.wait()

        data = Spheres(5, name='spheres')
        req = comm.isend(data, dest=1, tag=13)
        req.wait()

    elif rank == 1:
        req = comm.irecv(source=0, tag=11)
        data = req.wait()
        print(f'{rank=}: {data=}')
        assert data['a'] == 7
        assert data['b'] == 3.14

        req = comm.irecv(source=0, tag=12)
        data = req.wait()
        print(f'{rank=}: {data=}')
        assert data is None

        req = comm.irecv(source=0, tag=13)
        data = req.wait()
        print(f'{rank=}: {data=}')
        assert data.name == 'spheres'


if __name__ == "__main__":
    the_test_you_want_to_debug = test_PC_add_remove

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof