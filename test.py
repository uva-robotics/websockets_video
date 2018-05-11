import sys
import numpy as np
import cv2
from naoqi import ALProxy

import os
import StringIO
import sys
import time

import coils
import redis


# get NAOqi module proxy
videoDevice = ALProxy('ALVideoDevice', "192.168.1.10", 9559)

# subscribe top camera
AL_kTopCamera = 0
AL_kQVGA = 1            # 320x240
AL_kBGRColorSpace = 13
captureDevice = videoDevice.subscribeCamera("redis_cam20", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

print("GOT CAPTURE DEVICE")
# create image
width = 320
height = 240
image = np.zeros((height, width, 3), np.uint8)

store = redis.Redis()
fps = coils.RateTicker((1, 5, 10))

while True:

    # get image
    result = videoDevice.getImageRemote(captureDevice);

    if result == None:
        print 'cannot capture.'
    elif result[6] == None:
        print 'no image data string.'
    else:
        # translate value to mat
        values = map(ord, list(result[6]))

        print(len(values))
        n = np.array(values).reshape(240, 320, 3)
        # i = 0
        # for y in range(0, height):
        #     for x in range(0, width):
        #         image.itemset((y, x, 0), values[i + 0])
        #         image.itemset((y, x, 1), values[i + 1])
        #         image.itemset((y, x, 2), values[i + 2])
        #         i += 3

        # print(len(values), values)
        # a = np.zeros((height, width, 3))
        # x = np.reshape(result, (width, height)).T
        # print(x.shape, image.shape)
        # show image
        # cv2.imshow("pepper-top-camera-320x240", image)

        hello, encoded_image = cv2.imencode('.jpg', n)
        sio = StringIO.StringIO()
        np.save(sio, encoded_image)
        value = sio.getvalue()
        store.set('image', value)
        image_id = os.urandom(4)
        store.set('image_id', image_id)

        # Print the framerate.
        text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*fps.tick())
        print(text)

    # exit by [ESC]
    # if cv2.waitKey(33) == 27:
    #     break
