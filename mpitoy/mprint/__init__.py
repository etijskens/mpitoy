# -*- coding: utf-8 -*-

"""
Module mpitoy.mprint
==========================

A submodule for ...

"""

from mpi4py import MPI
comm = MPI.COMM_WORLD

def mprint(*args, **kwargs):
    print(f'[{comm.rank}]: ', *args, **kwargs)
