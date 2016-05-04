from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

from candle import position, state

camera = PiCamera()
rawCapture = PiRGBArray(camera)
time.sleep(1.0)
camera.capture(rawCapture, format="bgr")
img = rawCapture.array

found,x,y,w,h = position(img)
if found:
    print('Candle bounding box: (x,y)=(%d,%d), w=%d, h=%d ' % (x,y,w,h))
    lit = state(img,x,y,w,h)
    if lit:
        print('It seems to be ON')
    else:
        print('It seems to be OFF')
    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255),2)
else:
    print('No candle found in image')
    
cv2.imwrite("snapshot.png",img)
