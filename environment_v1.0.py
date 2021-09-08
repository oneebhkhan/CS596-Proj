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

	def __init__(self, version="2.0.0", integrator_type="path", max_depth="10"):
		self.scene = Element('scene')
		self.scene.set('version', "2.0.0")
		integrator = SubElement(self.scene, 'integrator', {'type':integrator_type} )
		SubElement(integrator, 'integer', {'name':"max_depth", 'value':max_depth})

	def addSensor(self, type="perspective", fov_value="45", translate=None, scale=None, \
		 rotate_axis="y", rotate_angle="180", sampler_type="independent", sample_count="32"):
		sensor = SubElement(self.scene, 'sensor', {'type':type})

		# add transformations
		transform = SubElement(sensor, 'transform', {'name':"to_world"})
		SubElement(transform, 'lookat', {'origin':"-3, 5, -20", 'target': "0, 0, 0", \
			 'up':"0, 1, 0"})
		# if translate:
		#     SubElement(transform, 'translate', {'value': translate})
		# if rotate_axis and rotate_angle:
		#     SubElement(transform, 'rotate', {rotate_axis: "1", "angle": rotate_angle})
		# if scale:
		#     SubElement(transform, 'scale', {'value': scale})

		# add sampler
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

environmentTree = ET.parse('Environment_Files/environment.xml')

root = environmentTree.getroot()

print("Tree", environmentTree)
print("Root", root)

# Emitter

shape = root.findall('shape')
occluder = ""
for item in shape:
	if item.attrib.get('id') == 'occluder':
		occluder = item

emitter = root.find('emitter')
emitter_vector = emitter.find('vector')
emitter_irradiance = emitter.find('spectrum')

point = occluder.find('point')

# Move the occluder in a radius
illumination = []
angle = []
irradiance = []
alpha = 1
radius_1, radius_2 = 100, 100

LA_LATITUDE = 34.052235
LA_LONGITUDE = -118.243683
x_arr = []
y_arr = []
z_arr = []
az_arr = []
elev_arr = []
start_date_time = "2021-09-07"
color_val = "#0000fe"
datetime_obj = datetime.datetime.fromisoformat(start_date_time)

while(alpha):
	
	alpha = 1

	datetime_obj += datetime.timedelta(days=1)
	color_val = hex(int(color_val[1:], base=16) + 40)
	color_val = "#"+str(color_val[2:])

	for hour_of_day in range(0,24,1):

		datetime_obj += datetime.timedelta(hours=1)

		az,zen = sunpos(datetime_obj,LA_LATITUDE,LA_LONGITUDE,0)[:2] #discard RA, dec, H
		#convert zenith to elevation
		elev = 90 - zen
		
		x_val = radius_1 * math.sin(math.radians(az))
		y_val = radius_1 * math.cos(math.radians(az))
		z_val = radius_2 * math.sin(math.radians(elev))

		x_arr.append(x_val)
		y_arr.append(y_val)
		z_arr.append(z_val)
		az_arr.append(az)
		elev_arr.append(elev)

		emitter_vector.set('value', str(x_val)+", "+str(y_val)+", "+str(z_val))
		# emitter_vector.set('value', "0, "+str(y_val)+", "+str(z_val))


		# INCREASING BRIGHTNESS OF SUN AS DAY PROGRESSES
		# if theta > 180:
		# 	irradiance_val = 2 *math.sin(math.radians(-1*theta)) + 1
		# 	print("IRRAD", irradiance)
		# 	irradiance.append(irradiance_val)
		# 	emitter_irradiance.set('value', str(irradiance_val))
		# else:
		irradiance.append(1)

		environmentTree.write('Environment_Files/environment.xml')

		CAMERA = 0
		RADMETER = 1

		scene = Scene()
		filename = 'Environment_Files/environment.xml'
		scene = load_file(filename)
		sensor = scene.sensors()[CAMERA]
		scene.integrator().render(scene, sensor)

		film = sensor.film()
		film.set_destination_file('Rendered_Files/environment.exr')
		film.develop()
		img = film.bitmap(raw=True).convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, \
			srgb_gamma=True)
		# img.write('Rendered_Files/'+filename+'.jpg')
		img.write('Rendered_Files/environment.jpg')
		
		
		# call the integrator again for the radmeter, and store its "film" output
		scene.integrator().render(scene, scene.sensors()[RADMETER])
		meter = scene.sensors()[RADMETER].film()

		rad = meter.bitmap(raw=True)
		rad_linear_Y = rad.convert(Bitmap.PixelFormat.Y, Struct.Type.Float32, \
			srgb_gamma=False)
		rad_np = np.array(rad_linear_Y)

		illumination.append(np.sum(rad_np))
		angle.append(az)

		fig_solar_motion = plt.figure()
		plt.scatter(angle, illumination, color='#44AA99', s=5)
		plt.scatter(angle, irradiance, color='purple', s=5)
		plt.title("ILLUMINANCE OF SUN")
		plt.xlabel("Azimuth Angle")
		plt.xlim([0,360])
		plt.ylim([0, 1600])
		# plt.grid()
		plt.ylabel("Illuminance")
		plt.savefig("Rendered_Files/Graphs/Illuminance_vs_Azimuth.png")
		print("\nTotal illumination on object is {}.\n".format(np.sum(rad_np)) )

		fig = plt.figure()
		ax = plt.axes(projection='3d')
		

		ax.scatter(xs=x_arr, ys=y_arr, zs=z_arr, zdir='z', s=20, c=color_val)
		
		ax.set_xticks([-100,-50,0,50,100])
		ax.set_yticks([-100,-50,0,50,100])
		ax.set_zticks([-50,-25,0,25,50])
		ax.axes.set_xlim3d(left=-100, right=100) 
		ax.axes.set_ylim3d(bottom=-100, top=100) 
		ax.axes.set_zlim3d(bottom=-75, top=75) 
		plt.savefig("Rendered_Files/Graphs/Solar_Motion.png")

		# fig, axs = plt.subplots(1, 3)
		# axs[0,0].scatter()



