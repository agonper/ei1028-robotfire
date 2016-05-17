import numpy
import threading
import time

# S = [230, 248, 266, 297, 350, 445, 680, 760]

# S_R = [217, 230, 252, 289, 330, 409, 588, 667]
# S_L = [218, 241, 286, 300, 332, 407, 577, 675]

S_R = [230, 241, 262, 294, 348, 455, 719, 740]
S_L = [239, 245, 258, 285, 341, 438, 700, 762]
D = [28, 24, 20, 16, 12, 8, 4, 3]


class WallAvoider:
    def __init__(self, robot, kill_signal):
        self._robot = robot
        self._kill_signal = kill_signal
        self._start_detecting()

    def move_without_crashing(self):
        robot = self._robot
        (lv, rv) = self._robot.distance()
        if not robot.error:
            (d_l, d_r) = WallAvoider.interpolate_distances((lv, rv))
            if 14 <= d_r < 28 and 14 <= d_l < 28:
                robot.motors(70, 70)
            elif d_r < 14:
                robot.motors(0, 60)
            elif d_l < 14:
                robot.motors(60, 0)
            elif d_r >= 28 and d_l >= 28:
                robot.motors(75, 40)
            else:
                if d_r < d_l:
                    robot.motors(40, 60)
                else:
                    robot.motors(60, 40)
        else:
            print('Error!')
            
    def _start_detecting(self):
        def detector(that):
            while True:
                if that._kill_signal.is_set():
                    print("killed")
                    break
                ultrasound = self._robot.ultrasound()
                if 5 < ultrasound < 15:
                    print(ultrasound)
                    self._robot.motors(-80, -80)
                time.sleep(0.1)

        threading.Thread(target=detector, args=(self,)).start()


    @staticmethod
    def interpolate_distances(sensor_values):
        (lv, rv) = sensor_values
        d_l = numpy.interp(lv, S_L, D)
        d_r = numpy.interp(rv, S_R, D)
        return [d_l, d_r]
