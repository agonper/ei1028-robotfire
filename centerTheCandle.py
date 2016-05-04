from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

from Robot2 import *
from candle import position

robot = Robot(ULTRASONIC_CONFIG)

camera = PiCamera()
stream = PiRGBArray(camera)
time.sleep(0.1)

try:
    converged = False
    while not converged:
        stream.truncate(0)
        camera.capture(stream, format='bgr')
        image = stream.array
        found,x,y,w,h = position(image)
        if found:
            xm = x + w/2
            dx = xm - 360
            motor = dx * 500 / 360
            if motor > 50:
                motor = 50
            if motor < -50:
                motor = -50
            print(xm,dx,motor)
            robot.motors(motor, -motor)
            time.sleep(0.1)
            robot.motors(0,0)
            converged = abs(motor) < 10
        else:
            print("candle not found")
except KeyboardInterrupt:
    pass
robot.terminate()