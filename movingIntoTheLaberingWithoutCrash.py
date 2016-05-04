from Robot2 import *
import numpy

S = [230, 248, 266, 297, 350, 445, 680, 760]
D = [28, 24, 20, 16, 12, 8, 4, 3]

robot = Robot(ULTRASONIC_CONFIG)
    
try:
    while True:
        (lV, rV) = robot.distance()
        if not robot.error:
            d = numpy.interp(rV,S,D)
            print(rV,d)
            if d>=16 and d<19:
                robot.motors(60, 60)
            elif d<16:
                robot.motors(0, 60)
            else:
                robot.motors(60, 40)
        else:
            print('Error!')             
        time.sleep(0.01)
except KeyboardInterrupt:
	pass
robot.terminate()