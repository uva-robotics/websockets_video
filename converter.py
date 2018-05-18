#!/usr/bin/python

from ws4py.client.threadedclient import WebSocketClient

import base64
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import threading
from Queue import Queue
import sys

import sensor_msgs.msg
import rospy

queue = Queue()

class Read(threading.Thread):

    _ENCODINGMAP_PY_TO_ROS = {'L': 'mono8', 'RGB': 'rgb8',
                              'RGBA': 'rgba8', 'YCbCr': 'yuv422'}

    _PIL_MODE_CHANNELS = {'L': 1, 'RGB': 3, 'RGBA': 4, 'YCbCr': 3}

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.publisher = rospy.Publisher('websockets_video', sensor_msgs.msg.Image, queue_size=10)

    def pil_to_ros(self, img):
        if img.mode == 'P':
            img = img.convert('RGB')

        rosimage = sensor_msgs.msg.Image()
        rosimage.encoding = self._ENCODINGMAP_PY_TO_ROS[img.mode]
        (rosimage.width, rosimage.height) = img.size
        rosimage.step = (self._PIL_MODE_CHANNELS[img.mode] * rosimage.width)
        rosimage.data = img.tobytes()
        return rosimage

    def run(self):
        while True:
            data = queue.get()
            print("RECEIVED DATA", sys.getsizeof(data))
            im = Image.open(BytesIO(base64.b64decode(data)))
            ros_img = self.pil_to_ros(im)
            self.publisher.publish(ros_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


class WSClient(WebSocketClient):

    def opened(self):
        self.send("*" * 1)

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, message):
        queue.put(str(message))
        self.send('1')

if __name__ == '__main__':
    try:
        rospy.init_node('websockets_video', anonymous=True)

        reader = Read()
        reader.start()

        ws = WSClient('ws://169.254.203.203:9000/ws')
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
