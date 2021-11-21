import sys
import os
import logging
import yaml
import math
import datetime 
import json
import time

import numpy as np
import gym
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d

import mitsuba
mitsuba.set_variant('scalar_rgb')
from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Feature_Libraries.sun_position import sunpos

from Environment_Files.xml_scene import XML_Scene
from Environment_Files.plant import Plant


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


	def step(self, action, rendering_bool=True, render_scene=True, irrad_meter_integrator=True):
		'''
		1. Take action - i.e. plant object w/ location
			Update XML File
		2. Render Mitsuba file for resolution per Day
		3. Use Mitsuba Integrator to get incident light per object
		- 
		4. Call on reward function to reap reward
		'''

		plant_type, plant_x_loc, plant_y_loc = action
		self.curr_step_num += 1

		if plant_type:
			new_plant = Plant(self.plant_info_dict[plant_type - 1], plant_x_loc, plant_y_loc)
			self.plant_arr.append(new_plant)
			self.num_plants += 1
			self.xml_scene.addPlant(species=new_plant.stage_name, translate=str(plant_x_loc) +", " + str(plant_y_loc) +", 0")

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

					plant_irrad_arr += self.render(render_scene=render_scene, irrad_meter_integrator=irrad_meter_integrator)
			
			#Optimize this portion
			for plant, incident_light in zip(self.plant_arr, plant_irrad_arr):
				plant.incident_light += incident_light
				plant.plant_grow()
		# print("\n")



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

		if irrad_meter_integrator:
			for PLANT_OBJ_RADMETER in range(1, len(self.mitsuba_scene.sensors())):
			# call the integrator again for the PLANT_OBJ_RADMETER, and store its "film" output
				self.mitsuba_scene.integrator().render(self.mitsuba_scene, self.mitsuba_scene.sensors()[PLANT_OBJ_RADMETER])
				meter = self.mitsuba_scene.sensors()[PLANT_OBJ_RADMETER].film()

				rad = meter.bitmap(raw=True)
				rad_linear_Y = rad.convert(Bitmap.PixelFormat.Y, Struct.Type.Float32, \
					srgb_gamma=False)
				rad_np = np.array(rad_linear_Y)

				curr_plant_irradiance = np.sum(rad_np)
				
				plant_irrad_arr.append(curr_plant_irradiance)
		else:
			plant_irrad_arr = np.zeros(len(self.mitsuba_scene.sensors())-1)

		return plant_irrad_arr
			
	
	def get_sun_coordinates(self, hours_timedelta):
		
		radius_1, radius_2 = 1, 1

		# self.curr_date_time += datetime.timedelta(days=1)
		
		self.curr_date_time += datetime.timedelta(hours=hours_timedelta)

		utc_date_time = self.curr_date_time.astimezone(datetime.timezone.utc)

		# print("CURR TIME: ", self.curr_date_time)
		# print("UTC TIME:", utc_date_time)

		az, zen = sunpos(utc_date_time, self.latitude, self.longitude, self.elevation)[:2] #discard RA, dec, H
		#convert zenith to elevation
		elev = 90 - zen
		
		x_val = radius_1 * math.sin(math.radians(az))
		y_val = radius_1 * math.cos(math.radians(az))
		z_val = radius_2 * math.sin(math.radians(elev))

		return x_val, y_val, z_val

	def get_reward(self):
		pass


