import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

class XML_Scene:
	
	def __init__(self, xml_filepath):
		self.environment_tree = ET.parse(xml_filepath)
		self.scene = self.environment_tree.getroot()

	def addPlant(self, species, translate, bsdf_type=None, rgb_reflectance=None):
		plant = SubElement(self.scene, 'shape', {'type':'obj'})
		SubElement(plant, 'string', {'name': "filename", 'value': "Object_Files/"+str(species)})
		transform = SubElement(plant, 'transform', {'name':"to_world"})
		# SubElement(transform, 'rotate', {'value':"1, 0, 0", 'angle':"-90"}) # plant should always face up
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

	def toxmlFile(self, filename):
		f = open(filename, "w")
		print(self.prettify(self.scene), file=f)

	def prettify(self, elem):
		"""
		Return a pretty-printed XML string for the Element.
		"""
		rough_string = ET.tostring(elem, 'utf-8')
		reparsed = minidom.parseString(rough_string)
		reparsed_string = reparsed.toprettyxml(indent=" "*4)
		reparsed_string = "".join([s for s in reparsed_string.strip().splitlines(True) if s.strip()])
	
		return reparsed_string		

	def addInteger(self, element, name, value):
		SubElement(element, 'integer', {'name':name, 'value':value})

	def addString(self, element, name, value):
		SubElement(element, 'string', {'name':name, 'value':value})

	# def addEmitter(self, type="directional", direction="0,0,1"):
	# 	emitter = SubElement(self.scene, 'emitter', {'type':type})
	# 	SubElement(emitter, 'spectrum', {'name':"irradiance", 'value':"1.0"})
	# 	SubElement(emitter, 'vector', {'name':"direction", 'value':direction})

	# def addSensor(self, type="perspective", fov_value="45", translate=None, scale=None, \
	# 	 rotate_axis="y", rotate_angle="180", sampler_type="independent", sample_count="32"):
	# 	sensor = SubElement(self.scene, 'sensor', {'type':type})
	# 	# add transformations
	# 	transform = SubElement(sensor, 'transform', {'name':"to_world"})
	# 	SubElement(transform, 'lookat', {'origin':"-3, 5, -20", 'target': "0, 0, 0", \
	# 		 'up':"0, 1, 0"})
	# 	sampler = SubElement(sensor, 'sampler', {'type': sampler_type})
	# 	SubElement(sampler, 'integer', {"name":"sample_count", "value":sample_count})

	# 	# Generate an EXR image at HD resolution
	# 	# Not sure what this does but including it for now since it is in example file
	# 	film = SubElement(sensor, 'film', {'type':"hdrfilm"})
	# 	SubElement(film, 'integer', {'name':'width', 'value':"1920"})
	# 	SubElement(film, 'integer', {'name':'height', 'value':"1080"})
