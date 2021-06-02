'''
What to do with import statements? Put them in the agent code?---that's what's going to
be run and call the code from other .py files
'''

import os
import numpy as np
import mitsuba
mitsuba.set_variant('scalar_rgb')

# In the rendering script these import statements came after setting the variant---
# Maybe that order is required? 
from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file


class Renderer:

	def __init__(self):
		self.scene = None
		self.film = None

	# Add the scene directory to the FileResolver's search path and load it
	# filename specified by agent code
	def load_scene(self, filename):
		Thread.thread().file_resolver().append(os.path.dirname(filename))
		self.scene = load_file(filename)

	# Call the scene's integrator to render the loaded scene, store as film	
	def integrate_scene(self, sensor_choice):
		#CAMERA = 0
		#RADMETER = 1
		scene.integrator().render(scene, scene.sensors()[sensor_choice])
		# consider writing film attribute as list which can store output from multiple sensors
		self.film = scene.sensors()[sensor_choice].film()

	# Write out rendering as OpenEXR file, tonemapped JPG optional
	def write_film(self, film=None, bitmap=False):
		if film is None:
			film = self.film
		film.set_destination_file('camera_output.exr')
		film.develop()
		if bitmap==True:
			bmp = film.bitmap(raw=True)
			bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write('camera_output.jpg')

# Get linear pixel values from the irradiance meter as a numpy array, summed
# pixel format specified as 'Y' should yield luminance-only values
# film should be result of irradiance meter integration!
def get_irradiance(film):
	rad = film.bitmap(raw=True)
	rad_linear_Y = rad.convert(Bitmap.PixelFormat.Y, Struct.Type.Float32, srgb_gamma=False)
	rad_np = np.array(rad_linear_Y)
	return np.sum(rad_np)

# Sets the desired mitsuba variant---we don't need anything other than scalar rgb I think
def set_mitsuba_variant(variant='scalar_rgb'):
	mitsuba.set_variant(variant)
