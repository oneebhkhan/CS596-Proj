import sys
import os
import logging
import yaml
import math
import datetime 
import json
import time
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import threading
import logging
# import concurrent.futures.Executor

import numpy as np
import gym
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d

from enoki import *
import mitsuba
mitsuba.set_variant('scalar_rgb')
from mitsuba.core import Bitmap, Struct, Thread, Logger, LogLevel
from mitsuba.core.xml import load_file
 
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Feature_Libraries.sun_position import sunpos

from Environment_Files.xml_scene import XML_Scene
from Environment_Files.plant import Plant

#// TODO: Join threads when returning	
#// TODO: Use concurrent.futures.ThreadPoolExecutor for multithreading
# TODO: Ensure there is no segmentation fault
# TODO: Run MPI4Py
# TODO: Change interactive job command
#// TODO: Determine time without printing logging information
#// TODO: Iterate over a different amount of threads and see which works best
# TODO: Run different threads 3 times to get an avg time
# TODO: mitsuba.set_variant('gpu_rgb')
# TODO: Run multithreaded instance on local m/c

'''
PENDING TASKS:
- CREATE 2D ARRAY REPRESENTATION FOR OBSERVATION SPACE
- DESIGN REWARD FUNCTION
- LOOK INTO REMOVING COMMAND LINE PROMPTS FROM MITSUBA
- ENSURE CORRECT PLACEMENT OF HORIZON
DONE - PLOT OUT TIME TAKEN FOR ONE EPISODE
DONE - MAKE SURE SUN STARTS AT THE RIGHT POSITION
DONE - FORMAT XML CORRECTLY
DONE - NO RENDERING IF SUN BELOW HORIZON
DONE - LOAD PLANT OBJECTS FROM FILE
DONE - USE RELATIVE FILE PATHS
DONE - REMOVE MODIFIED XML FILE WHEN ENV.CLOSE IS CALLED
DONE - SEPARATE CLASSES INTO INDIVIDUAL FILES
DONE - CONTROL GRANULARITY OF DAY
DONE - INCORPORATE DAY WITHIN STEP FUNCTION
DONE - USE YAML CONFIG FILE
'''

'''
* Save nn.torch.seed
'''
class AgroEnv(gym.Env):

	def __init__(self):
		# super(AgroEnv, self).__init__()
		self.dirname = os.path.dirname(__file__)
		
		with open('configuration.yaml') as configuration_yaml_file:
			configuration_dict = yaml.full_load(configuration_yaml_file)
		self.start_date_time = configuration_dict["START_DATE"]
		self.latitude = configuration_dict["LATITUDE"]
		self.longitude = configuration_dict["LONGITUDE"]
		self.elevation = configuration_dict["ELEVATION"]
		self.time_steps_per_day = configuration_dict["DAY_SIZE_RESOLUTION"]
		self.empty_environment_path = os.path.join(self.dirname, configuration_dict["EMPTY_XML_FILEPATH"])
		self.modified_environment_path = os.path.join(self.dirname, configuration_dict["MODIFIED_XML_FILEPATH"])
		self.exr_environment_path = os.path.join(self.dirname, configuration_dict["EXR_FILEPATH"])
		self.jpg_environment_path = os.path.join(self.dirname, configuration_dict["JPG_FILEPATH"])
		self.plant_info_path = os.path.join(self.dirname, configuration_dict["PLANT_INFO_FILEPATH"])
		self.obj_file_path = os.path.join(self.dirname, configuration_dict["OBJ_FILEPATH"])
		self.graph_file_path = os.path.join(self.dirname, configuration_dict["GRAPH_FILEPATH"])

		self.xml_scene = XML_Scene(self.empty_environment_path)
		self.mitsuba_scene = None
		self.curr_step_num = 0
		self.total_step_num = 365
		self.curr_date_time = datetime.datetime.fromisoformat(self.start_date_time)

		plant_json_file = open(self.plant_info_path)
		self.plant_info_dict = json.load(plant_json_file)

		self.plant_arr = [] #Array of Plants planted so far

		self.num_plants = 0

		self.plant_irrad_dict = dict()
		self.mitsuba_threads = list()
		self.lock = threading.Lock()
		self.counter = 0
		# Define action and observation space
		# They must be gym.spaces objects
		self.action_space = []
		self.observation_space = [] #List of floating point x, y loc of each plant

		self.done = False


	def reset(self):
		'''
		1. Set XML file to be an empty field with the environment objects as desired (e.g. occluder)
		2. Set steps = 0
		3. Set calendar date
		'''
		self.xml_scene = XML_Scene('Environment_Files/empty_environment.xml')
		self.mitsuba_scene = None
		self.curr_step_num = 0
		self.num_plants = 0

		self.curr_date_time = datetime.datetime.fromisoformat(self.start_date_time)
		self.plant_arr = []
		self.done = False


	def close(self):
		os.remove(self.modified_environment_path)


	def add_plant_to_scene(self, action):
		plant_type, plant_x_loc, plant_y_loc = action

		if plant_type:
			new_plant = Plant(self.plant_info_dict[plant_type - 1], plant_x_loc, plant_y_loc)
			self.plant_arr.append(new_plant)
			self.num_plants += 1
			self.xml_scene.addPlant(species=new_plant.stage_name, translate=str(plant_x_loc) +", " + str(plant_y_loc) +", 0")


	def step(self, action, rendering_bool=True, render_scene=True, irrad_meter_integrator=True):
		'''
		1. Take action - i.e. plant object w/ location
			Update XML File
		2. Render Mitsuba file for resolution per Day
		3. Use Mitsuba Integrator to get incident light per object
		- 
		4. Call on reward function to reap reward
		'''
		Thread.thread().logger().set_log_level(LogLevel.Warn)
		
		# plant_type, plant_x_loc, plant_y_loc = action
		self.curr_step_num += 1

		self.add_plant_to_scene(action)
		if rendering_bool:
			emitter_vector = self.xml_scene.scene.find('emitter').find('vector')
			
			day_loop = np.arange(0, 24, 24/self.time_steps_per_day)
			plant_irrad_arr = np.zeros(self.num_plants) 

			for hour_of_day in day_loop:

				x_val, y_val, z_val = self.get_sun_coordinates(24/self.time_steps_per_day)

				# print("HOUR OF DAY: ", hour_of_day, self.curr_date_time)
				# print("X_VAL", x_val, "Y_VAL", y_val, "Z_VAL", z_val,"\n")

				if z_val >= 0:

					emitter_vector.set('value', str(x_val)+", "+str(y_val)+", "+str(z_val))
					
					self.xml_scene.toxmlFile(self.modified_environment_path)
					self.mitsuba_scene = load_file(self.modified_environment_path)

					plant_irrad_arr += self.render()
			
			#Optimize this portion
			for plant, incident_light in zip(self.plant_arr, plant_irrad_arr):
				plant.incident_light += incident_light
				plant.plant_grow()


	def render(self, render_scene=True, irrad_meter_integrator=True):
		CAMERA = 0
	
		sensor = self.mitsuba_scene.sensors()[CAMERA]
		self.mitsuba_scene.integrator().render(self.mitsuba_scene, sensor)

		if render_scene:
			film = sensor.film()
			film.set_destination_file(self.exr_environment_path)
			film.develop()
			img = film.bitmap(raw=True).convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, \
				srgb_gamma=True)
			img.write(self.jpg_environment_path)

		plant_irrad_arr =[]
		
		#* INTRODUCE MULTI THREADING HERE
		if irrad_meter_integrator:
			python_threads = list()
			
			mainThread = Thread.thread()
			saved_fresolver = mainThread.file_resolver()
			saved_logger = mainThread.logger()
			# print("Main Thread ID:", Thread.thread_id())
			# input()
			
			# for RADMETER_INDEX in range(1, 5):
			total_thread_num = 200
			with ThreadPoolExecutor(max_workers=total_thread_num) as executor:
				futures_iter = []
				for thread_num in range(1, total_thread_num+1):
					futures_iter.append(executor.submit(self.worker_func, thread_num, total_thread_num, saved_fresolver, saved_logger))
				
				for future in as_completed(futures_iter):
					future.result()
				
				# call the integrator again for the RADMETER_INDEX, and store its "film" output
				# x = threading.Thread(target=self.worker_func, args=(self.mitsuba_scene, thread_num, total_thread_num, saved_fresolver, saved_logger))
				# python_threads.append(x)
				# x.start()

			# for index, x in enumerate(python_threads):
			# 	x.join()
			# time.sleep(10)
			# python_threads = []
			# wait(, return_when='ALL_COMPLETED')
			
			
			for key in sorted(self.plant_irrad_dict.keys()):
				plant_irrad_arr.append(self.plant_irrad_dict[key])

		else:
			plant_irrad_arr = np.zeros(len(self.mitsuba_scene.sensors())-1)
		
		print("Active count", threading.active_count())

		return plant_irrad_arr

	def worker_func(self, thread_num, total_threads, saved_fresolver, saved_logger):
		Thread.register_external_thread('render_'+str(thread_num)) 
		newThread = Thread.thread()
		newThread.set_file_resolver(saved_fresolver) 
		newThread.set_logger(saved_logger)

		self.calculate_plant_irradiance(thread_num, total_threads)
		# Thread.join()

	
	def calculate_plant_irradiance(self, thread_num, total_threads):
		for radmeter_index in range(thread_num, 501, total_threads):		
			self.mitsuba_scene.integrator().render(self.mitsuba_scene, self.mitsuba_scene.sensors()[radmeter_index])
			meter = self.mitsuba_scene.sensors()[radmeter_index].film()
			rad = meter.bitmap(raw=True)
			rad_linear_Y = rad.convert(Bitmap.PixelFormat.Y, Struct.Type.Float32, \
				srgb_gamma=False)
			rad_np = np.array(rad_linear_Y)
			curr_plant_irradiance = np.sum(rad_np)
			self.plant_irrad_dict[radmeter_index-1] = curr_plant_irradiance
	

	def get_sun_coordinates(self, hours_timedelta):
		
		radius_1, radius_2 = 1, 1

		self.curr_date_time += datetime.timedelta(hours=hours_timedelta)

		utc_date_time = self.curr_date_time.astimezone(datetime.timezone.utc)

		# print("CURR TIME: ", self.curr_date_time)
		# print("UTC TIME:", utc_date_time)

		az, zen = sunpos(utc_date_time, self.latitude, self.longitude, self.elevation)[:2] #* INFO: discard RA, dec, H

		#* INFO: convert zenith to elevation
		elev = 90 - zen
		
		x_val = radius_1 * math.sin(math.radians(az))
		y_val = radius_1 * math.cos(math.radians(az))
		z_val = radius_2 * math.sin(math.radians(elev))

		return x_val, y_val, z_val

	def get_reward(self):
		pass


