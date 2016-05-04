from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import threading
import numpy

from Robot2 import *
from candle import position

S = [230, 248, 266, 297, 350, 445, 680, 760]
D = [28, 24, 20, 16, 12, 8, 4, 3]

corridor_event = threading.Event()

def centerTheCandle(camera, stream, robot):
    while True:
		light = robot.light()
		print("Light: " + str(light))
		if light < 530:
			print("LINE DETECTED")
			corridor_event.clear()
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
					
					robot.motors(motor, -motor)
					time.sleep(0.1)
					robot.motors(0,0)
					converged = abs(motor) < 10
					print("candle found")
				else:
					print("candle not found")
			
			# corridor_event.clear()
		time.sleep(0.1)

def movingIntoTheLaberint(robot):
    while True:
		if not corridor_event.isSet():
			corridor_event.wait()
		
		(lV, rV) = robot.distance()
		if not robot.error:
			d = numpy.interp(rV,S,D)
			
			if d>=16 and d<19:
				robot.motors(60, 60)
			elif d<16:
				robot.motors(0, 60)
			else:
				robot.motors(60, 40)
		else:
			print('Error!')             
		time.sleep(0.1)

def main():
	try:
		robot = Robot(ULTRASONIC_CONFIG)
		camera = PiCamera()
		stream = PiRGBArray(camera)
		
		corridor_event.set()
		moving = threading.Thread(target=movingIntoTheLaberint, args=(robot,))
		centeringCandle = threading.Thread(target=centerTheCandle, args=(camera, stream, robot))

		moving.start()
		centeringCandle.start()
        
	except KeyboardInterrupt:
		robot.terminate()
		camera.close()
		print("END")

if __name__=="__main__":
    main()
