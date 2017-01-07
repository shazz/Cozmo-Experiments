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

def test():
    image1 = Image.open("test2.jpg")
    #resized_image1 = image1.resize((299, 299), Image.LANCZOS)
    image1.save("tmp1.jpg", "JPEG")
	
    image2 = Image.open("test3.jpg")
    #resized_image2 = image2.resize((299, 299), Image.LANCZOS)
    image2.save("tmp2.jpg", "JPEG")

    image3 = Image.open("test4.jpg")
    #resized_image3 = image3.resize((299, 299), Image.LANCZOS)
    image3.save("tmp3.jpg", "JPEG")

    start = time.process_time()	
    recognized_object, score = run_inference_on_file("tmp1.jpg")
    print("this is a", recognized_object, "in", (time.process_time()- start), "s with score", score)
	
    start = time.process_time()		
    recognized_object, score = run_inference_on_file("tmp2.jpg")
    print("this is a", recognized_object, "in", (time.process_time()- start), "s with score", score)

    start = time.process_time()	
    recognized_object, score = run_inference_on_file("tmp3.jpg")
    print("this is a", recognized_object, "in", (time.process_time()- start), "s with score", score)

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
    
 
