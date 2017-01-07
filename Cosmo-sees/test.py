#!/usr/bin/env python3

from PIL import Image
import tensorflow as tf
from classify_image import init_classifier
from classify_image import run_inference_on_file

import time

def test():
    image1 = Image.open("save2.jpg")
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

if __name__ == '__main__':
    init_classifier()
    test()
 
