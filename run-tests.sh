#!/bin/bash

pytest tests/mpitoy

mpirun -np 3 python -m pytest tests_mpi/mpitoy/ --with-mpi