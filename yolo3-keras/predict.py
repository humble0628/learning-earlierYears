from nets.yolo3 import yolo_body
from keras.layers import Input
import keras
import tensorflow as tf
import os
from yolo import YOLO
from PIL import Image

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
keras.backend.tensorflow_backend.set_session(tf.Session(config=config))

yolo = YOLO()


while True:
    img = input('Input image filename:')
    try:
        image = Image.open(img)
    except:
        print('Open Error! Try again!')
        continue
    else:
        r_image = yolo.detect_image(image)
        r_image.show()
yolo.close_session()
