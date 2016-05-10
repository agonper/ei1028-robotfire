import numpy
import time

S_R = [217, 230, 252, 289, 330, 409, 588, 667]
S_L = [218, 241, 286, 300, 332, 407, 577, 675]

S = [230, 248, 266, 297, 350, 445, 680, 760]
D = [28, 24, 20, 16, 12, 8, 4, 3]


class WallAvoider:
    def __init__(self, robot):
        self._robot = robot

    def move_without_crashing(self):
        robot = self._robot
        (lv, rv) = robot.distance()
        if not robot.error:
            d_r = numpy.interp(rv, S_R, D)
            d_l = numpy.interp(lv, S_L, D)

            if 13 <= d_r < 28 and 13 <= d_l < 28:
                robot.motors(70, 70)
            elif d_r < 13:
                robot.motors(0, 70)
            elif d_l < 13:
                robot.motors(70, 0)
            else:
                if d_r < d_l:
                    robot.motors(45, 70)
                else:
                    robot.motors(70, 45)
        else:
            print('Error!')
