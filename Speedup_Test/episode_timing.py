import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Environment_Files.gym_mitsuba_env import AgroEnv
from matplotlib import pyplot as plt

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
	


if __name__ == "__main__":

	episode_time_test()
	# step_time_test()
