import sys
import os
import numpy as np
import mitsuba
mitsuba.set_variant('scalar_spectral')

from mitsuba.core.xml import load_file
from mitsuba.core import Bitmap, Struct, Thread
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET

# In the rendering script these import statements came after setting the variant---
# Maybe that order is required?


class Scene:

    def __init__(self, version="2.0.0", integrator_type="path", max_depth="10"):
        self.scene = Element('scene')
        self.scene.set('version', "2.0.0")
        integrator = SubElement(self.scene, 'integrator', {
                                'type': integrator_type})
        SubElement(integrator, 'integer', {
                   'name': "max_depth", 'value': max_depth})

    def addSensor(self, type="perspective", fov_value="45", translate=None, scale=None, rotate_axis="y", rotate_angle="180", sampler_type="independent", sample_count="32"):
        sensor = SubElement(self.scene, 'sensor', {'type': type})

        # add transformations
        transform = SubElement(sensor, 'transform', {'name': "to_world"})
        SubElement(transform, 'lookat', {
                   'origin': "-3, 5, -20", 'target': "0, 0, 0", 'up': "0, 1, 0"})
        # if translate:
        #     SubElement(transform, 'translate', {'value': translate})
        # if rotate_axis and rotate_angle:
        #     SubElement(transform, 'rotate', {rotate_axis: "1", "angle": rotate_angle})
        # if scale:
        #     SubElement(transform, 'scale', {'value': scale})

        # add sampler
        sampler = SubElement(sensor, 'sampler', {'type': sampler_type})
        SubElement(sampler, 'integer', {
                   "name": "sample_count", "value": sample_count})

        # Generate an EXR image at HD resolution
        # Not sure what this does but including it for now since it is in example file
        film = SubElement(sensor, 'film', {'type': "hdrfilm"})
        SubElement(film, 'integer', {'name': 'width', 'value': "1920"})
        SubElement(film, 'integer', {'name': 'height', 'value': "1080"})

    def addSphere(self, center, radius, bsdf_type=None, rgb_reflectance=None):
        x, y, z = center
        sphere = SubElement(self.scene, 'shape', {'type': "sphere"})
        SubElement(sphere, 'point', {
                   'name': "center", 'x': str(x), 'y': str(y), 'z': str(z)})
        SubElement(sphere, 'float', {'name': "radius", "value": str(radius)})
        if bsdf_type:
            bsdf = SubElement(sphere, 'bsdf', {'type': bsdf_type})
            if rgb_reflectance:
                SubElement(bsdf, 'rgb', {
                           'name': "reflectance", 'value': rgb_reflectance})

    def addPlant(self, species="Corn1.obj", translate=None, bsdf_type=None, rgb_reflectance=None):
        plant = SubElement(self.scene, 'shape', {'type': 'obj'})
        SubElement(plant, 'string', {'name': "filename", 'value': species})
        transform = SubElement(plant, 'transform', {'name': "to_world"})
        # plant should always face up
        SubElement(transform, 'rotate', {'value': "1, 0, 0", 'angle': "-90"})
        if translate:
            SubElement(transform, 'translate', {'value': translate})
        if bsdf_type:
            bsdf = SubElement(sphere, 'bsdf', {'type': bsdf_type})
            if rgb_reflectance:
                SubElement(bsdf, 'rgb', {
                           'name': "reflectance", 'value': rgb_reflectance})

    def addIrradianceMeter(self, object, sampler_type="stratified", sample_count="16"):
        element = self.scene.find(object)
        sensor = SubElement(element, 'sensor', {'type': 'irradiancemeter'})
        sampler = SubElement(sensor, 'sampler', {'type': sampler_type})
        SubElement(sampler, 'integer', {
                   'name': "sample_count", 'value': str(sample_count)})
        film = SubElement(sensor, 'film', {'type': "hdrfilm"})
        self.addInteger(film, "width", "100")
        self.addInteger(film, "height", "100")
        self.addString(film, "pixel_format", "luminance")
        SubElement(film, 'rfilter', {'type': "box"})

    def addEmitter(self, type="directional", direction="0,0,1"):
        emitter = SubElement(self.scene, 'emitter', {'type': type})
        SubElement(emitter, 'spectrum', {'name': "irradiance", 'value': "1.0"})
        SubElement(emitter, 'vector', {
                   'name': "direction", 'value': direction})

    def addInteger(self, element, name, value):
        SubElement(element, 'integer', {'name': name, 'value': value})

    def addString(self, element, name, value):
        SubElement(element, 'string', {'name': name, 'value': value})

    def toxmlFile(self, filename):
        f = open(filename, "w")
        print(prettify(self.scene), file=f)

    # code from Renderer class

    # def __init__(self):
    #     self.scene = None
    #     self.film = None

    #     # Add the scene directory to the FileResolver's search path and load it
    #     # filename specified by agent code
    # def load_scene(self, filename):
    #     Thread.thread().file_resolver().append(os.path.dirname(filename))
    #     self.scene = load_file(filename)

    #     # Call the scene's integrator to render the loaded scene, store as film

    # def integrate_scene(self, sensor_choice):
    #     # CAMERA = 0
    #     # RADMETER = 1
    #     scene.integrator().render(scene, scene.sensors()[sensor_choice])
    #     # consider writing film attribute as list which can store output from multiple sensors
    #     self.film = scene.sensors()[sensor_choice].film()

    # # Write out rendering as OpenEXR file, tonemapped JPG optional

    # def write_film(self, film=self.film, bitmap=False):
    #     film.set_destination_file('camera_output.exr')
    #     film.develop()
    #     if bitmap == True:
    #         bmp = film.bitmap(raw=True)
    #         bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8,
    #                     srgb_gamma=True).write('camera_output.jpg')

    #     # Get linear pixel values from the irradiance meter as a numpy array, summed
    #     # pixel format specified as 'Y' should yield luminance-only values
    #     # film should be result of irradiance meter integration!
    # def get_irradiance(self, film):
    #     rad = film.bitmap(raw=True)
    #     rad_linear_Y = rad.convert(
    #         Bitmap.PixelFormat.Y, Struct.Type.Float32, srgb_gamma=False)
    #     rad_np = np.array(rad_linear_Y)
    #     return np.sum(rad_np)

# Sets the desired mitsuba variant---we don't need anything other than scalar rgb I think
# this should just be called at the top of the agent code---no need to include it here
# def set_mitsuba_variant(variant='scalar_rgb'):
#	mitsuba.set_variant(variant)


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def main():
    scene = Scene()
    scene.addSensor()
    scene.addSphere((0, 0, 0), .27, "diffuse", ".9, .9, .9")
    scene.addIrradianceMeter('shape')
    scene.addEmitter()
    print(prettify(scene.scene))
    scene.toxmlFile("test.xml")


main()
