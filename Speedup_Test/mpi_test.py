from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


if rank == 0:
	print("rank", rank)
	print("size", size)
	data = {'a': 7, 'b': 3.14}
	comm.send(data, dest=1, tag=11)
elif rank == 1:
	data = comm.recv(source=0, tag=11)
	print("Data",data)