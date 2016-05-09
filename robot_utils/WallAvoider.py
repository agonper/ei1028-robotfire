import numpy
import time

S = [230, 248, 266, 297, 350, 445, 680, 760]
D = [28, 24, 20, 16, 12, 8, 4, 3]


class WallAvoider:
    def __init__(self, robot):
        self._robot = robot

    def move_without_crashing(self):
        robot = self._robot
        (lv, rv) = robot.distance()
        if not robot.error:
            d = numpy.interp(rv, S, D)

            if 16 <= d < 19:
                robot.motors(60, 60)
            elif d < 16:
                robot.motors(0, 60)
            else:
                robot.motors(60, 40)
        else:
            print('Error!')