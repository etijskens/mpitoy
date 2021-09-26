# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'.')

"""MPI tests for mpitoy.simulation package."""
import pytest

@pytest.mark.mpi(min_size=2)
def test_size():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    print(comm.size)
    assert comm.size >= 2

# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_size

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof