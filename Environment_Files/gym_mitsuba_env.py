import sys
import os
import numpy as np
import gym
import mitsuba
import logging
import yaml

from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
mitsuba.set_variant('scalar_rgb')
import datetime 

from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file
import math
from Feature_Libraries.sun_position import sunpos

from xml_scene import XML_Scene
from plant import Plant

'''
PENDING TASKS:
- USE RELATIVE FILE PATHS
- FORMAT XML CORRECTLY
- REMOVE MODIFIED XML FILE WHEN ENV.CLOSE IS CALLED
- LOAD PLANT OBJECTS FROM FILE
- CREATE 2D ARRAY REPRESENTATION
- DESIGN REWARD FUNCTION
- SEPARATE CLASSES INTO INDIVIDUAL FILES
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
		self.xml_scene = XML_Scene('Environment_Files/empty_environment.xml')
		self.mitsuba_scene = None
		self.curr_step_num = 0
		self.total_step_num = 365
		
		with open('configuration.yaml') as configuration_yaml_file:
			configuration_dict = yaml.full_load(configuration_yaml_file)
		self.start_date_time = configuration_dict["START_DATE"]
		self.latitude = configuration_dict["LATITUDE"]
		self.longitude = configuration_dict["LONGITUDE"]
		self.elevation = configuration_dict["ELEVATION"]
		self.time_steps_per_day = configuration_dict["DAY_SIZE_RESOLUTION"]

		self.curr_date_time = datetime.datetime.fromisoformat(self.start_date_time)

		self.plant_arr = ["Corn1.obj"]
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

		self.curr_date_time = datetime.datetime.fromisoformat(self.start_date_time)

		self.done = False


	def close(self) -> None:
		pass


	def step(self, action):
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
			self.num_plants += 1
			self.xml_scene.addPlant(species=self.plant_arr[plant_type - 1], translate=str(plant_x_loc) +", " + str(plant_y_loc) +", 0")

		emitter_vector = self.xml_scene.scene.find('emitter').find('vector')
		
		day_loop = np.arange(0, 24, 24/self.time_steps_per_day)
		plant_irrad_arr = np.zeros(self.num_plants) 

		for hour_of_day in day_loop:

			x_val, y_val, z_val = self.get_sun_coordinates(24/self.time_steps_per_day)

			emitter_vector.set('value', str(x_val)+", "+str(y_val)+", "+str(z_val))
			
			self.xml_scene.toxmlFile('Environment_Files/test.xml')
			self.mitsuba_scene = load_file('Environment_Files/test.xml')

			plant_irrad_arr += self.render()

		print("PIA",plant_irrad_arr)


	def render(self):
		CAMERA = 0
	
		sensor = self.mitsuba_scene.sensors()[CAMERA]
		self.mitsuba_scene.integrator().render(self.mitsuba_scene, sensor)

		film = sensor.film()
		film.set_destination_file('Rendered_Files/field.exr')
		film.develop()
		img = film.bitmap(raw=True).convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, \
			srgb_gamma=True)
		# img.write('Rendered_Files/'+filename+'.jpg')
		img.write('Rendered_Files/field.jpg')

		plant_irrad_arr =[]

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

		return plant_irrad_arr
			
	
	def get_sun_coordinates(self, hours_timedelta):
		
		radius_1, radius_2 = 100, 100

		# self.curr_date_time += datetime.timedelta(days=1)
		
		self.curr_date_time += datetime.timedelta(hours=hours_timedelta)

		az, zen = sunpos(self.curr_date_time, self.latitude, self.longitude, self.elevation)[:2] #discard RA, dec, H
		#convert zenith to elevation
		elev = 90 - zen
		
		x_val = radius_1 * math.sin(math.radians(az))
		y_val = radius_1 * math.cos(math.radians(az))
		z_val = radius_2 * math.sin(math.radians(elev))

		return x_val, y_val, z_val

	def get_reward(self):
		pass


NewEnv = AgroEnv()
NewEnv.step([1,2,1])
print("\n\n", NewEnv.curr_date_time)
NewEnv.step([1,10,1])
print("\n\n", NewEnv.curr_date_time)