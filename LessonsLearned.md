## Lessons learned 

### Messages to send

For each boundary plane of a domain, for each PC in that domain, for each array in that PC, 
for leaving and ghost particles, there will be a send and a recv operation across that 
boundary to the neighbouring domain. (presumably, this will happen at almost every timestep).

             domain n   boundary   domain n+1
    aimulation              |             s imulation
      |                     |                     |
     PC                     |                     PC
      |                     |                     |
      +-- Array1 +-- send --|-> recv --+ Array1 --+
      |          +-- recv --|-> recv --+          | 
      +-- Array2 +-- send --|-> recv --+ Array2 --+
                 +-- recv --|-> recv --+ 

This can be achieved by creating a communication functor for every particle container, 
which in turn creates a communication functor for each array. The array communiation
functor must store: 
- the tag to be used, 
- a send and recv buffer, 
- a reference to the array object, 
- a reference to the list of indices to be send, to fill the send buffer with the 
  correct elements. This list is obviously the same for all arrays of a particle
  container, and should be stored by the particle container communication functor
- When the first array update is received, a list of empty elements must be created
  that serves as the locations of the received elements. This list must be accessible
  by the other arrays of the same particle container when their updates are received. 
  It seems best to store this in the particle container communication functor. The 
  list can only be created after the first array is received.

So, for every boundary in a domain, there will be two particle container communication 
functors, one for communicating the particles that move across the boundary, and one for 
the ghost particles. The ghost particle container is peculiar.

### Communicating ghost particles

The communication functor for ghost particles is different because the particle container
receiving the particles is not the same particle container on both sides of the domain,
the receiving particle container is the ghost particle container of the sending particle
container. Hence, we need a mechanism to pair a particle container and its ghost particle
container. At first sight, making the ghost particle container a child of the particle
container seems practical.

If we insist on communicating only changes in the ghost particle container, we must 
communicate two lists: the new ghost particles and the ghost particles that must be removed.
It is best to first communicate the particles that must be removed because in this way, they
free memory space for the new ghosts. Communication of the ghost particles that must be removed 
requires communicating the list. There are particle arrays to be communicated. 

### Tags are important, or not ...

When the array updates are sent/received with **non-blocking** messages, the message tag
is essential for pairing the sends and recvs, as there may be many sends and receives
simultaneously active. The difficulty is two-fold:
- the tag must be unique for the message during the period in which tag collisions 
  may happen. As time steps are separated by and MPI barrier the tags can be reused the 
  next timestep. 
- both the sender and its corresponding receiver must have the same tag, in order for the
  receiver to pick up the correct message.

If the message is blocking, tags are not an issue. However, instead it is essential that 
the order of the messages is the same on all processes. (This might be more difficult to
guarantee and if sth goes wrong, it will be hard to debug.)
That is, if domain _n_ send an update for array1 to domain _n+1_, then domain 
must first receive it and than send its update for array1 to domain _n_. This 
requirement is automatically satisfied with mpi_sendrecv. The order in which the 
different arrays are threated must be the same on both domains, though.

There are two possibilites to make sure that the sender and the receiver have the same tag:
1. both the sender and receiver construct the tag from information that is **shared between
   processes**, e.g. an the name or id of the array and of the particle container. Obviously,
   this can only work if these properties are indeed the same in all (neighbouring) processes.
   
2. The sender constructs a unique tag and communicates it to the receiver using blocking 
   communication (non-blocking communication would raise the tag problem again). Note 
   this requires that the order of the sends and receives must match. That is, when all even 
   ranks are sending, all odd ranks must receive. Alternatively, `sendrecv` can be used
   to avoid deadlocking. The pointer of the sending object is by definition unique and could
   in principle be used as a tag. 

###### Caveat
Using `id(object)` (the equivalent of a pointer in Python) in Python yielded 
`OverflowError: value too large to convert to int`. 
The size of a Python `int` is larger than the size of the `int` type used by MPI.
This might happen in C++ as well. The size of a pointer in C++ is 8 bytes (for 64bit OS).
The MPI `int` may be only 4 bytes.

The alternative that was tested was using a simple "tag factory" which can provide tags
that were not used before. This uses tag i for sending to the right and receiving from the 
left, and tag i-1 for sending to the left and receiving from the right. Tags must be only 
send to the right and received from the left, as the tag for the other direction can be 
derived. This seems to work well and reduces the number of tags to be communicate by a
factort (as the tag for right to left communication is the tag for left to right communication
minus one).

Broad casting the tag is also an option, as message are further discriminated by source and 
destination. the tag factory must then be instatiated only once.

   
### avoid deadlocks with mpi_sendrecv

Combined sendrecv (mpi_sendrecv) is usefull to implement the communication across a boundary,
as this communication is symmetric: there is always a send and receive on both sides. When
blocking communication is used and the sends and recvs are ordered in the same way in  
neighbouring domains the program will deadlock. mpi_sendrecv avoids this.

### Dynamically adjusting buffer size on the receiver side

The receiver can probe the message to satisfy the required buffer size, before actually 
the message. See 
- http://www.mathcs.emory.edu/~cheung/Courses/355/Syllabus/92-MPI/send+recv-adv.html
- https://mpitutorial.com/tutorials/dynamic-receiving-with-mpi-probe-and-mpi-status/

### Spreading communication across threads in an MPI process (to be solved later)

Clearly, this entails many messages. If they are executed serially, this 
might imply a lot of wasted cycles. Mpacts will supposedly run in a hybrid environment 
OpenMP/MPI environment. At a later stage this communication may be executed in an OpenMP 
parallel section (or parallellized with TBB), as to handle the communication and their
pre- and post-processing in parallel. This requires sending messages between threads in 
an MPI program. Check the PRACE course "Hybrid CPU programming with OpenMP and MPI" for 
how to do this (https://events.prace-ri.eu/event/1225/).

### How many MPI processes per node? (to be solved later)

The obvious options are:

1. one per node
2. one per socket
3. one per NUMA domain (in combination with pinning of memory)
4. one per core (implying serial processes)
   
From option 1 to 4 the number of message becomes smaller. The size of the messages is
more or less the same (In 1D domain decompositions there will be more boundaries, but
the boundaries are typically not smaller. This is different in 2D or 3D domain composition).

It is logical to start with the first option.

The PRACE course "Hybrid CPU programming with OpenMP and MPI" 
mentions these potential advantages of the hybrid approach:
1. Fewer MPI processes for a given amount of cores
   1. Improved load balance (?)
   2. All-to-all communication bottlenecks alleviated
   3. Decreased memory consumption if an implementation uses replicated data 
2. Additional parallelization levels may be available 
3. Possibility for dedicating threads to different tasks, e.g. thread dedicated to 
   communication or parallel I/O
4. Dynamic parallelization patterns often easier to implement with OpenMP

   