import xml.etree.ElementTree as etree
import xml.dom.minidom
import xml.etree.ElementTree as ET

import subprocess

import numpy as np
import math
import mitsuba
mitsuba.set_variant('scalar_rgb')
from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file


rotations = np.linspace(
    start=0.0,
    stop=360.0,
    num=100,
    endpoint=False
)

for (frame, rotation) in enumerate(rotations, 1):
	print(frame, rotation)
	xml_filepath = "Animation_Files/colored_500_plants_rotation.xml"
	# mitsuba_scene = load_file("Environment_Files/500_plants_rotation.xml")

	environment_tree = ET.parse(xml_filepath)
	scene = environment_tree.getroot()

	camera_postion = scene.find('sensor').find('transform').find('lookat')

	x_val = 350*math.cos(math.radians(rotation))
	y_val = 350*math.sin(math.radians(rotation))

	camera_postion.set('origin', str(x_val)+", "+str(y_val)+", 150")

	rough_string = ET.tostring(scene, 'utf-8')
	reparsed = xml.dom.minidom.parseString(rough_string)
	reparsed_string = reparsed.toprettyxml(indent=" "*4)
	reparsed_string = "".join([s for s in reparsed_string.strip().splitlines(True) if s.strip()])

	with open("Animation_Files/colored_500_plants_rotation.xml", "w") as field_xml:
		field_xml.write(reparsed_string)

	CAMERA = 0
	mitsuba_scene = load_file("Animation_Files/colored_500_plants_rotation.xml")
	sensor = mitsuba_scene.sensors()[CAMERA]
	mitsuba_scene.integrator().render(mitsuba_scene, sensor)

	film = sensor.film()
	# film.set_destination_file(self.exr_environment_path)
	# film.develop()
	img = film.bitmap(raw=True).convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, \
		srgb_gamma=True)
	img.write("Animation_Files/images/field_python_{n:02d}.png".format(n=frame))