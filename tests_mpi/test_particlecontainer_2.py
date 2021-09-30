# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')

"""Tests for mpitoy package."""

from mpitoy import Spheres

import pytest

@pytest.mark.mpi(min_size=2)
def test():
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
    test()
    print('-*# finished #*-')

# eof