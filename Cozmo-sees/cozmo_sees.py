import os
import asyncio
import cozmo
import time

# image manipulation
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Cannot import from PIL. Do `pip3 install --user Pillow` to install")

# Tensorflow
from classify_image import download_classifier, run_inference_on_file, setup_classifier

# Run Configuration
os.environ['COZMO_PROTOCOL_LOG_LEVEL'] = 'DEBUG'
os.environ['COZMO_LOG_LEVEL'] = 'DEBUG'
USE_VIEWER = True
USE_LOGGING = False
USE_FILTER = True
CUBE_SEARCH_TIMEOUT = 3
DISPLAY_TEXT_DURATION = 0.75
PURPLE = cozmo.lights.Color(rgba=(138, 43, 226 , 255))
GREEN = cozmo.lights.Color(rgba=(0, 255, 0, 255))
ORANGE = cozmo.lights.Color(rgba=(255, 165, 0, 255))

'''
Cozmo Sees
-Experimenting with Cozmo's camera and Google Tensorflow Machine Learning framework
-Use Google's Inception v3 pretrained model


@author Shazz
@author Cozplay team for base python framework
'''

_font = None
try:
    _font = ImageFont.truetype("arial.ttf", 20)
except IOError:
    try:
        _font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 20)
    except IOError:
        pass

def make_text_image(text_to_draw, x, y, font=None):
    # make a blank image for the text, initialized to opaque black
    text_image = Image.new('RGBA', cozmo.oled_face.dimensions(), (0, 0, 0, 255))
    dc = ImageDraw.Draw(text_image)
    dc.text((x, y), text_to_draw, fill=(255, 255, 255, 255), font=font)

    return text_image

class CozmoSees:
    def __init__(self):
        self._count = 0
        self._cube = 0
        self._robot = None
        self._is_busy = False
        self._last_image = None
        if USE_LOGGING:
            cozmo.setup_basic_logging()
        if USE_VIEWER:
            cozmo.connect_with_tkviewer(self.run)
        else:
            cozmo.connect(self.run)

    async def set_up_cozmo(self, coz_conn):
        print('setup classifier')
        setup_classifier()
        print("Looking for the cube")
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

        print("cube found")
        await self._robot.play_anim("anim_reacttoblock_happydetermined_01").wait_for_completed()
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=34.5)).wait_for_completed()
        await self._robot.say_text("Hey. Tap the cube", duration_scalar=1.2).wait_for_completed()
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=0.0)).wait_for_completed()
        self._cube.color = PURPLE
        self._robot.world.add_event_handler(cozmo.objects.EvtObjectTapped, self.on_object_tapped)

    async def on_object_tapped(self, event, *, obj, tap_count, tap_duration, **kw):
        print("cube tapped")
        if self._is_busy:
            print("Cozmo is busy")
            return
        else:
            print("Cozmo can check now")
            self._is_busy = True
            self._cube.color = ORANGE
            await self.classify_vision()
            self._is_busy = False

    # Classify the VGA Camera raw image with Tensorflow
    async def classify_vision(self):
        
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=0)).wait_for_completed()

        self._cube.color = GREEN

        while self._last_image is None:
            self._last_image = self._robot.world.latest_image
            print("image = %s" % self._last_image)
            time.sleep(0.1)     
        #resized_image = self._last_image.raw_image.resize((100, 100), Image.LANCZOS)
        #resized_image.save("tmp.jpg", "JPEG")
        self._last_image.raw_image.save("tmp.jpg", "JPEG")
        self._last_image = None
        
        recognized_object, score = run_inference_on_file("tmp.jpg")
        print(recognized_object,':', score)

        await self._robot.play_anim("anim_hiking_edgesquintgetin_01").wait_for_completed()
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=44.5)).wait_for_completed()

        if score < 0.2:
            await self._robot.say_text("I didn't see anything interesting.", duration_scalar=1.2).wait_for_completed()
        elif score > 0.2:
            text_img = make_text_image(recognized_object.split(',')[0], 8, 6, _font)
            oled_face_data = cozmo.oled_face.convert_image_to_screen_data(text_img)
            await self._robot.display_oled_face_image(oled_face_data, 3000.0).wait_for_completed()            
            await self._robot.say_text("I think I see a " + recognized_object.split(',')[0], duration_scalar=1.2).wait_for_completed()
            await self._robot.play_anim("anim_memorymatch_pointcenter_02").wait_for_completed()            

        await self._robot.say_text("Show mw something !", duration_scalar=1.2).wait_for_completed()
        await self._robot.set_head_angle(cozmo.util.Angle(degrees=0.0)).wait_for_completed()

        self._cube.color = PURPLE

    async def run(self, coz_conn):
        # Set up Cozmo
        await self.set_up_cozmo(coz_conn)

        while True:
            await asyncio.sleep(0)
        pass


class CozmoSeesCube(cozmo.objects.LightCube):
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
    download_classifier()
    cozmo.world.World.light_cube_factory = CozmoSeesCube
    CozmoSees()