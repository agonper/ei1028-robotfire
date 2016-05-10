import time
import Candle
from robot_utils.RobotMain import RobotStatus
from robot_utils.WallAvoider import *

class RobotSide:
    Left = 0
    Right = 1

    @staticmethod
    def get_closer_to(side):
        if side == RobotSide.Left:
            return -40, 40
        if side == RobotSide.Right:
            return 40, -40

class RoomController:
    def __init__(self, robot, camera, stream):
        self._robot = robot
        self._camera = camera
        self._stream = stream

    def extinguish_fire(self):
        stream = self._stream
        camera = self._camera
        robot = self._robot

        converged = False
        while not converged:
            stream.truncate(0)
            camera.capture(stream, format='bgr')
            image = stream.array
            found, x, y, w, h = Candle.position(image)

            if found:
                xm = x + w / 2
                dx = xm - 360
                motor = dx * 500 / 360
                if motor > 50:
                    motor = 50
                if motor < -50:
                    motor = -50

                robot.motors(motor, -motor)
                time.sleep(0.1)
                robot.motors(0, 0)
                converged = abs(motor) < 10
                print("candle found")
            else:
                print("candle not found")

        assert False is True, "Implement this!!"
        # TODO Once converged move up to a safe distance within the candle and extinguish the fire

    def evaluate_room(self):
        robot = self._robot

        distances = self._calculate_distances()
        farthest_side = RobotSide.Right
        if distances[RobotSide.Left] > distances[RobotSide.Right]:
            farthest_side = RobotSide.Left

        while distances[farthest_side] > 15:
            self._stream.truncate(0)
            self._camera.capture(self._stream, format='bgr')
            image = self._stream.array

            found, x, y, w, h = Candle.position(image)
            if found:
                robot.motors(0, 0)
                print("Candle found!!")
                return RobotStatus.FIRE_ROOM
            robot.motors(RobotSide.get_closer_to(farthest_side))

            distances = self._calculate_distances()
            time.sleep(0.2)
        print("No candle found")

        return RobotStatus.EMPTY_ROOM

    def _calculate_distances(self):
        (lv, rv) = self._robot.distance()
        while self._robot.error:
            (lv, rv) = self._robot.distance()
        (d_l, d_r) = WallAvoider.interpolate_distances((lv, rv))
        return [d_l, d_r]
