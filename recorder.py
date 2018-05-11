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

import Image

videoDevice = ALProxy('ALVideoDevice', "192.168.1.10", 9559)

AL_kTopCamera = 0
AL_kQVGA = 1 # 320x2480
AL_kBGRColorSpace = 13
captureDevice = videoDevice.subscribeCamera("redis_cam1", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

width = 320
height = 240
image = np.zeros((height, width, 3), np.uint8)

store = redis.Redis()
fps = coils.RateTicker((1, 5, 10))

total_time = 0
while True:
    print("CYCLE TIME", time.time() - total_time)
    total_time = time.time()

    start_time = time.time()
    result = videoDevice.getImageRemote(captureDevice);
    print("EXEC TIME VIDEO: {}".format(time.time() - start_time))

    if result == None:
        print 'cannot capture.'
    elif result[6] == None:
        print 'no image data string.'
    else:
        # translate value to mat

        # start_time = time.time()
        # values = map(ord, list(result[6]))
        # print("EXEC TIME MAP: {}".format(time.time() - start_time))

        start_time = time.time()
        n = Image.frombytes("RGB", (width, height), result[6])
        print("EXEC TIME NP: {}".format(time.time() - start_time))
        # start_time = time.time()
        # reshape = n.reshape(height, width, 3)
        # print("EXEC TIME NP RESHAPE: {}".format(time.time() - start_time))

        encode_time = time.time()
        open_cv_image = np.array(n)
        hello, encoded_image = cv2.imencode('.jpg', open_cv_image)

        sio = StringIO.StringIO()
        np.save(sio, encoded_image)
        # print("ENCODE TIME", time.time() - encode_time)
        #
        redis_time = time.time()
        value = sio.getvalue()
        store.set('image', value)
        image_id = os.urandom(4)
        store.set('image_id', image_id)
        # print("REDIS TIME ", time.time() - redis_time)
        # text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*fps.tick())
        # print(text)
