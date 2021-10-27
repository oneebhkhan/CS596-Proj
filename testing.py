import sys
import os
import numpy as np
import mitsuba
import logging
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
GOALS:
1. Simulate motion of the sun
2. Simulate cloud motion
'''

class Scene:

	def __init__(self, xml_filepath, version="2.0.0", integrator_type="path", max_depth="10"):
		self.environment_tree = ET.parse(xml_filepath)
		self.scene = self.environment_tree.getroot()
		# self.scene.set('version', "2.0.0")
		# integrator = SubElement(self.scene, 'integrator', {'type':integrator_type} )
		# SubElement(integrator, 'integer', {'name':"max_depth", 'value':max_depth})

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
				
	def addPlant(self, species="Corn1.obj", translate=None, bsdf_type=None, \
		 gb_reflectance=None):
		plant = SubElement(self.scene, 'shape', {'type':'obj'})
		SubElement(plant, 'string', {'name': "filename", 'value':species})
		transform = SubElement(plant, 'transform', {'name':"to_world"})
		SubElement(transform, 'rotate', {'value':"1, 0, 0", 'angle':"-90"}) # plant should always face up
		if translate:
			SubElement(transform, 'translate', {'value': translate})
		if bsdf_type:
			bsdf = SubElement(sphere, 'bsdf', {'type':bsdf_type})
			if rgb_reflectance:
				SubElement(bsdf, 'rgb', {'name':"reflectance", 'value': rgb_reflectance})

	def addIrradianceMeter(self, object, sampler_type="stratified", sample_count="16"):
		element = self.scene.find(object)
		sensor = SubElement(element, 'sensor', {'type':'irradiancemeter'})
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
		print(prettify(self.scene), file=f)


def prettify(elem):
	"""Return a pretty-printed XML string for the Element.
	"""
	rough_string = ET.tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")

environmentTree = ET.parse('Mitsuba-AG-Agent(r)/Environment_Files/environment.xml')

root = environmentTree.getroot()

environmentTree1 = ET.parse('Mitsuba-AG-Agent(r)/Environment_Files/environment.xml')

root1 = environmentTree.getroot()


print("Tree", environmentTree)
print("Root", root)
print("Tree1", environmentTree1)
print("Root1", root1)

scene_obj = Scene(xml_filepath='Mitsuba-AG-Agent(r)/Environment_Files/environment.xml')

print(scene_obj.environment_tree)
print(scene_obj.scene)


# # Emitter

# shape = root.findall('shape')
# occluder = ""
# for item in shape:
# 	if item.attrib.get('id') == 'occluder':
# 		occluder = item

# emitter = root.find('emitter')
# emitter_vector = emitter.find('vector')
# emitter_irradiance = emitter.find('spectrum')

# point = occluder.find('point')

# # Move the occluder in a radius
# illumination = []
# angle = []
# irradiance = []
# alpha = 1
# radius_1, radius_2 = 100, 100

# LA_LATITUDE = 34.052235
# LA_LONGITUDE = -118.243683
# x_arr = []
# y_arr = []
# z_arr = []
# az_arr = []
# elev_arr = []
# start_date_time = "2021-09-07"
# color_val = "#0000fe"
# datetime_obj = datetime.datetime.fromisoformat(start_date_time)



# CAMERA = 0
# RADMETER = 1

# scene = Scene()
# filename = 'Environment_Files/environment.xml'
# scene = load_file(filename)
# sensor = scene.sensors()[CAMERA]
# scene.integrator().render(scene, sensor)

# film = sensor.film()
# film.set_destination_file('Rendered_Files/environment.exr')
# film.develop()
# img = film.bitmap(raw=True).convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, \
# 	srgb_gamma=True)
# # img.write('Rendered_Files/'+filename+'.jpg')
# img.write('Rendered_Files/environment.jpg')


# # call the integrator again for the radmeter, and store its "film" output
# scene.integrator().render(scene, scene.sensors()[RADMETER])
# meter = scene.sensors()[RADMETER].film()

# rad = meter.bitmap(raw=True)
# rad_linear_Y = rad.convert(Bitmap.PixelFormat.Y, Struct.Type.Float32, \
# 	srgb_gamma=False)
# rad_np = np.array(rad_linear_Y)

# print("\nTotal illumination on object is {}.\n".format(np.sum(rad_np)) )
