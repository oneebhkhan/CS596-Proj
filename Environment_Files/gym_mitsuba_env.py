import sys
import os
import numpy as np
import gym
# from yaml import load
import mitsuba
import logging
# import yaml
# import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
mitsuba.set_variant('scalar_rgb')
import datetime 

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file
import math
from Feature_Libraries.sun_position import sunpos
'''
PENDING TASKS:
- USE RELATIVE FILE PATHS
- FORMAT XML CORRECTLY
- REMOVE MODIFIED XML FILE WHEN ENV.CLOSE IS CALLED
- INCORPORATE DAY WITHIN STEP FUNCTION
- USE YAML CONFIG FILE
- LOAD PLANT OBJECTS FROM FILE
- CREATE 2D ARRAY REPRESENTATION
- DESIGN REWARD FUNCTION
'''


class Plant:
	def __init__(self, plant_name):
		self.name = plant_name
		self.x_loc = 0
		self.y_loc = 0
		self.harvest_age = 0
		self.space_requirement = 0
		self.incident_light = 0
		self.light_requirement = 0

		

class XML_Scene:
	
	def __init__(self, xml_filepath):
		self.environment_tree = ET.parse(xml_filepath)
		self.scene = self.environment_tree.getroot()

	def addSensor(self, type="perspective", fov_value="45", translate=None, scale=None, \
		 rotate_axis="y", rotate_angle="180", sampler_type="independent", sample_count="32"):
		sensor = SubElement(self.scene, 'sensor', {'type':type})
		# add transformations
		transform = SubElement(sensor, 'transform', {'name':"to_world"})
		SubElement(transform, 'lookat', {'origin':"-3, 5, -20", 'target': "0, 0, 0", \
			 'up':"0, 1, 0"})
		sampler = SubElement(sensor, 'sampler', {'type': sampler_type})
		SubElement(sampler, 'integer', {"name":"sample_count", "value":sample_count})

		# Generate an EXR image at HD resolution
		# Not sure what this does but including it for now since it is in example file
		film = SubElement(sensor, 'film', {'type':"hdrfilm"})
		SubElement(film, 'integer', {'name':'width', 'value':"1920"})
		SubElement(film, 'integer', {'name':'height', 'value':"1080"})

	def addSphere(self, center, radius, bsdf_type=None, rgb_reflectance=None):
		x, y, z = center
		sphere = SubElement(self.scene, 'shape', {'type':"sphere"})
		SubElement(sphere, 'point', {'name': "center", 'x':str(x),'y':str(y),'z':str(z)})
		SubElement(sphere, 'float', {'name':"radius", "value":str(radius)})
		if bsdf_type:
			bsdf = SubElement(sphere, 'bsdf', {'type':bsdf_type})
			if rgb_reflectance:
				SubElement(bsdf, 'rgb', {'name':"reflectance", 'value': rgb_reflectance})
				

	def addPlant(self, species, translate, bsdf_type=None, rgb_reflectance=None):
		plant = SubElement(self.scene, 'shape', {'type':'obj'})
		SubElement(plant, 'string', {'name': "filename", 'value': "Object_Files/"+str(species)})
		transform = SubElement(plant, 'transform', {'name':"to_world"})
		SubElement(transform, 'rotate', {'value':"1, 0, 0", 'angle':"-90"}) # plant should always face up
		SubElement(transform, 'translate', {'value': translate})
		
		if bsdf_type:
			bsdf = SubElement(plant, 'bsdf', {'type':bsdf_type})
			if rgb_reflectance:
				SubElement(bsdf, 'rgb', {'name':"reflectance", 'value': rgb_reflectance})
		
		self.addIrradianceMeter(plant)
		


	def addIrradianceMeter(self, object, sampler_type="stratified", sample_count="16"):
		# element = self.scene.find(object)
		sensor = SubElement(object, 'sensor', {'type':'irradiancemeter'})
		sampler = SubElement(sensor, 'sampler', {'type':sampler_type})
		SubElement(sampler, 'integer', {'name':"sample_count", 'value':str(sample_count)})
		film=SubElement(sensor, 'film', {'type':"hdrfilm"})
		self.addInteger(film, "width", "100")
		self.addInteger(film, "height", "100")
		self.addString(film, "pixel_format", "luminance")
		SubElement(film, 'rfilter', {'type':"box"})


	def addEmitter(self, type="directional", direction="0,0,1"):
		emitter = SubElement(self.scene, 'emitter', {'type':type})
		SubElement(emitter, 'spectrum', {'name':"irradiance", 'value':"1.0"})
		SubElement(emitter, 'vector', {'name':"direction", 'value':direction})
	
	def addInteger(self, element, name, value):
		SubElement(element, 'integer', {'name':name, 'value':value})
	def addString(self, element, name, value):
		SubElement(element, 'string', {'name':name, 'value':value})


	def toxmlFile(self, filename):
		f = open(filename, "w")
		print(self.prettify(self.scene), file=f)

	def prettify(self, elem):
		"""Return a pretty-printed XML string for the Element.
		"""
		rough_string = ET.tostring(elem, 'utf-8')
		reparsed = minidom.parseString(rough_string)
		return reparsed.toprettyxml(indent="")		

'''
* Save nn.torch.seed
'''
class AgroEnv(gym.Env):

	def __init__(self):
		# super(AgroEnv, self).__init__()
		START_DATE_TIME = "2021-09-07" # To be loaded from YAML FILE
		LA_LATITUDE = 34.052235  # To be loaded from YAML FILE
		LA_LONGITUDE = -118.243683  # To be loaded from YAML FILE

		self.xml_scene = XML_Scene('Environment_Files/empty_environment.xml')
		self.mitsuba_scene = None
		self.curr_step_num = 0
		self.total_step_num = 365
		
		# with open('../configuration.yaml') as configuration_yaml_file:
		# 	configuration_dict = yaml.full_load(configuration_yaml_file)
		self.start_date_time = START_DATE_TIME
		self.latitude = LA_LATITUDE
		self.longitude = LA_LONGITUDE
		self.elevation = 0.0

		self.curr_date_time = datetime.datetime.fromisoformat(self.start_date_time)

		self.plant_arr = ["Corn1.obj"]
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
		4. Call on reward function to reap reward
		'''
		plant_type, plant_x_loc, plant_y_loc = action
		self.xml_scene.addPlant(species=self.plant_arr[plant_type], translate=str(plant_x_loc) +", " + str(plant_y_loc) +", 0")
		
		emitter_vector = self.xml_scene.scene.find('emitter').find('vector')
		for hour_of_day in range(24):

			x_val, y_val, z_val = self.get_sun_coordinates()


			emitter_vector.set('value', str(x_val)+", "+str(y_val)+", "+str(z_val))
			
			self.xml_scene.toxmlFile('Environment_Files/test.xml')
			self.mitsuba_scene = load_file('Environment_Files/test.xml')

			self.render()

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

		for PLANT_OBJ_RADMETER in range(1, len(self.mitsuba_scene.sensors())):
		# call the integrator again for the PLANT_OBJ_RADMETER, and store its "film" output
			self.mitsuba_scene.integrator().render(self.mitsuba_scene, self.mitsuba_scene.sensors()[PLANT_OBJ_RADMETER])
			meter = self.mitsuba_scene.sensors()[PLANT_OBJ_RADMETER].film()

			rad = meter.bitmap(raw=True)
			rad_linear_Y = rad.convert(Bitmap.PixelFormat.Y, Struct.Type.Float32, \
				srgb_gamma=False)
			rad_np = np.array(rad_linear_Y)

			curr_plant_irradiance = np.sum(rad_np)
			
			print("AFTER INTEGRATING\n", curr_plant_irradiance) # ADD THIS TO PLANT OBJECT'S ACCUMULATED LIGHT
			
	
	def get_sun_coordinates(self):
		
		radius_1, radius_2 = 100, 100

		# self.curr_date_time += datetime.timedelta(days=1)
		
		self.curr_date_time += datetime.timedelta(hours=1)

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
NewEnv.step([0,2,1])
NewEnv.step([0,10,1])