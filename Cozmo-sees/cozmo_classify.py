#!/usr/bin/env python3

# Ask Cozmo to tell what he sees...

'''cozmo_classify


- Get the last raw image that Cozmo saw
- transform the raw image
- call imagenet classifier
- get the msot probable result
- Request Cozmo to say the name
'''

import sys
import asyncio
import cozmo

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Cannot import from PIL. Do `pip3 install --user Pillow` to install")

from classify_image import init_classifier
from classify_image import run_inference_on_file

import time

# get a font - location depends on OS so try a couple of options
# failing that the default of None will just use a default font
_clock_font = None
try:
    _clock_font = ImageFont.truetype("arial.ttf", 20)
except IOError:
    try:
        _clock_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 20)
    except IOError:
        pass

class CozmoSees:
    def __init__(self):
        self._count = 0
        self._cube = 0
        self._robot = None
        self._is_busy = False
        if USE_LOGGING:
            cozmo.setup_basic_logging()
        if USE_VIEWER:
            cozmo.connect_with_tkviewer(self.run)
        else:
            cozmo.connect(self.run)

async def set_up_cozmo(self, coz_conn):
        asyncio.set_event_loop(coz_conn._loop)
        self._robot = await coz_conn.wait_for_robot()
        self._robot.camera.image_stream_enabled = True
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=0)).wait_for_completed()
        try:
            cubes = await self._robot.world.wait_until_observe_num_objects(1, cozmo.objects.LightCube)
            self._cube = cubes[0]
        except TimeoutError:
            print("Could not find cube")
            return False
        await self._robot.play_anim("anim_reacttoblock_happydetermined_01").wait_for_completed()
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=44.5)).wait_for_completed()
        await self._robot.say_text("Hey. Tap the cube and I'll investigate", duration_scalar=1.2).wait_for_completed()
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=0.0)).wait_for_completed()
        self._cube.color = PURPLE
        self._robot.world.add_event_handler(cozmo.objects.EvtObjectTapped, self.on_object_tapped)

async def on_object_tapped(self, event, *, obj, tap_count, tap_duration, **kw):
    if self._is_busy:
        return
    else:
        self._is_busy = True
        self._cube.color = ORANGE
        response = await self.send_label_request()
        if response:
            await self.process_label_response(response)
        self._is_busy = False


class CloudVisionCube(cozmo.objects.LightCube):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._color = cozmo.lights.off

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: cozmo.lights.Color):
        self._color = value
        self.set_lights(cozmo.lights.Light(value))

if __name__ == '__main__':
    cozmo.world.World.light_cube_factory = CloudVisionCube
    CozmoSees()        

def make_text_image(text_to_draw, x, y, font=None):
    '''Make a PIL.Image with the given text printed on it

    Args:
        text_to_draw (string): the text to draw to the image
        x (int): x pixel location
        y (int): y pixel location
        font (PIL.ImageFont): the font to use

    Returns:
        :class:(`PIL.Image.Image`): a PIL image with the text drawn on it
    '''

    # make a blank image for the text, initialized to opaque black
    text_image = Image.new('RGBA', cozmo.oled_face.dimensions(), (0, 0, 0, 255))

    # get a drawing context
    dc = ImageDraw.Draw(text_image)

    # draw the text
    dc.text((x, y), text_to_draw, fill=(255, 255, 255, 255), font=font)

    return text_image

async def run(self, coz_conn):
    # Set up Cozmo
    await self.set_up_cozmo(coz_conn)

    while True:
        await asyncio.sleep(0)
    pass

def run(sdk_conn):
    '''The run method runs once Cozmo is connected.'''
    
    try:
        robot = sdk_conn.wait_for_robot()
        
        robot.camera.image_stream_enabled = True
        image = None
        while image is None:
            image = robot.world.latest_image
            print("image = %s" % image)
            time.sleep(0.1)       

        # now we have an image
        #if we need to resize ?
        resized_image = image.raw_image.resize((100, 100), Image.LANCZOS)
        resized_image.save("tmp.jpg", "JPEG")
        
        recognized_object, score = run_inference_on_file("tmp.jpg")
        print(recognized_object,':', score)
        if score > 0.3:
            obj_str = recognized_object.split(',')[0]
            say_text = "I see a"
            text_img = make_text_image(obj_str, 8, 6, _clock_font)
            oled_face_data = cozmo.oled_face.convert_image_to_screen_data(text_img)
            robot.display_oled_face_image(oled_face_data, 3000.0).wait_for_completed()
        else:
            obj_str = ""
            say_text = "I donno ???"

        robot.say_text(say_text + obj_str).wait_for_completed()
    
    except 	asyncio.TimeoutError as e:
        sys.exit("Cannot get Robot instance" % e)

def reconnect():
    cozmo.setup_basic_logging()
    try:
        cozmo.connect_with_tkviewer(run)
        #cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

if __name__ == '__main__':
    reconnect()
    
 
