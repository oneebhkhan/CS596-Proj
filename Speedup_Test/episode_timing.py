import sys
import os
import time
import threading
import pickle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from Environment_Files.gym_mitsuba_env_mpi4py import AgroEnv
# from Environment_Files.gym_mitsuba_env_multithreaded import AgroEnv
from Environment_Files.gym_mitsuba_env import AgroEnv
from matplotlib import pyplot as plt
import faulthandler
from mpi4py import MPI
from mpi4py import rc
rc.thread_level = "multiple"

from time_profile import TimeProfiler, TimeRecorder 

def episode_time_test():
	NewEnv = AgroEnv()
	time_arr = []
	step_arr = []

	episode_start_time = time.time()
	for step in range(20):
		
		if step < 180:
			plant_bool = 1
			plant_xloc = -step
			plant_yloc = -step
		else:
			plant_bool = 0
			plant_xloc = step
			plant_yloc = step

		step_start_time = time.time()
		NewEnv.step([plant_bool, plant_xloc, plant_yloc])
		step_end_time = time.time()

		time_arr.append(step_end_time-step_start_time)
		step_arr.append(step)

		plt.figure(dpi=200)
		plt.bar(step_arr, time_arr)
		plt.xlabel("Step Number")
		plt.ylabel("Time Taken (s)")
		plt.title("Time Taken per Step in one Training Episode")
		plt.savefig(NewEnv.graph_file_path + "Time_Taken_Per_Step.png")
		plt.clf()

	episode_end_time = time.time()

	print("Total Time Taken: ",episode_end_time-episode_start_time, "s")

	plt.close()

def step_time_test():
	NewEnv = AgroEnv()

	for plant_ind in range(10):
	
		NewEnv.step([1,plant_ind, plant_ind], False)

	time_arr = []
	step_arr = []

	for i in range(2):
		step_start_time = time.time()
		NewEnv.step([0,0,0])
		step_end_time = time.time()

		time_arr.append(step_end_time-step_start_time)
		step_arr.append("Both"+str(i+1))

	NewEnv.reset()

	for plant_ind in range(10):
	
		NewEnv.step([1,plant_ind, plant_ind], False)

	for i in range(2):
		step_start_time = time.time()
		NewEnv.step([0,0,0], render_scene=False)
		step_end_time = time.time()

		time_arr.append(step_end_time-step_start_time)
		step_arr.append("!Scene"+str(i+1))

	NewEnv.reset()

	for plant_ind in range(10):
	
		NewEnv.step([1,plant_ind, plant_ind], False)
		
	for i in range(2):
		step_start_time = time.time()
		NewEnv.step([0,0,0], irrad_meter_integrator=False)
		step_end_time = time.time()

		time_arr.append(step_end_time-step_start_time)
		step_arr.append("!Irrad"+str(i+1))

	NewEnv.reset()

	for plant_ind in range(10):
	
		NewEnv.step([1,plant_ind, plant_ind], False)

	for i in range(2):
		step_start_time = time.time()
		NewEnv.step([0,0,0], render_scene=False, irrad_meter_integrator=False)
		step_end_time = time.time()

		time_arr.append(step_end_time-step_start_time)
		step_arr.append("!Both"+str(i+1))
		
	plt.figure(dpi=200, figsize=[6,6])

	plt.bar(step_arr, time_arr,color=['blue', 'blue', 'green', 'green', 'red', 'red', 'black', 'black'])
	plt.title("Step Time Comparison w/ 10 Plants")
	plt.xlabel("Step Type")
	plt.ylabel("Time Taken(s)")
	plt.savefig(NewEnv.graph_file_path+"step_time_comparison.png")
	plt.close()
	
def plant_test_500_mpi(comm):
	with open('Speedup_Test/test_plant_loc.pickle', 'rb') as handle:
   		plant_loc_dict = pickle.load(handle)

	x_loc_arr = plant_loc_dict["X_LOC"]
	y_loc_arr = plant_loc_dict["Y_LOC"]

	test_env = AgroEnv()

	for x_loc, y_loc in zip(plant_loc_dict["X_LOC"], plant_loc_dict["Y_LOC"]):
		test_env.add_plant_to_scene([1, x_loc, y_loc])
	
	start_time = time.time()

	rank = comm.Get_rank()
	size = comm.Get_size()
	print("Size", size)
	print("Rank", rank)
	test_env.step([0,0,0], rank, size)
	
	# test_env.MPI_Test(comm, rank)

	print("Time taken: ", time.time()-start_time)
	print("Active Count after Step:", threading.active_count())
	# sys.exit()

def plant_test_500():
	tt = TimeProfiler('Main','plant_test_500()')
	with open('Speedup_Test/test_plant_loc.pickle', 'rb') as handle:
   		plant_loc_dict = pickle.load(handle)

	x_loc_arr = plant_loc_dict["X_LOC"]
	y_loc_arr = plant_loc_dict["Y_LOC"]

	test_env = AgroEnv()

	for x_loc, y_loc in zip(plant_loc_dict["X_LOC"], plant_loc_dict["Y_LOC"]):
		test_env.add_plant_to_scene([1, x_loc, y_loc])
	
	start_time = time.time()

	test_env.step([0,0,0])
	
	print("Time taken: ", time.time()-start_time)
	print("Active Count after Step:", threading.active_count())
	tr = TimeRecorder()
	tr.show_all()
	return


def plant_animation():
	with open('Speedup_Test/test_plant_loc.pickle', 'rb') as handle:
   		plant_loc_dict = pickle.load(handle)

	x_loc_arr = plant_loc_dict["X_LOC"]
	y_loc_arr = plant_loc_dict["Y_LOC"]

	test_env = AgroEnv()

	for x_loc, y_loc in zip(plant_loc_dict["X_LOC"], plant_loc_dict["Y_LOC"]):
		test_env.add_plant_to_scene([1, x_loc, y_loc], "diffuse", "0.015, 0.1, 0.027")

	test_env.xml_scene.toxmlFile('Animation_Files/colored_500_plants_rotation.xml')

if __name__ == "__main__":

	print(threading.active_count())
	faulthandler.enable()

	# for i in range(100):
	# 	print(i)
	# 	time.sleep(2)
	# 	plant_test_500()	
	# sys.exit()
	comm = MPI.COMM_WORLD
	
	# for i in range(10):
	# 	print("ITER",i)
	# 	time.sleep(2)
	# 	plant_test_500_mpi(comm)	

	# plant_test_500_mpi(comm)

	# plant_test_500()
	plant_animation()
	

