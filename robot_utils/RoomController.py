from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import Candle
import numpy
from robot_utils.RobotMain import RobotStatus
from robot_utils.WallAvoider import *


class RoomController:
    def __init__(self, robot):
        self._robot = robot
        self._camera = PiCamera()
        self._stream = PiRGBArray(self._camera)

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
        print("Evaluating room")
        stream = self._stream
        camera = self._camera
        robot = self._robot

        print("Local variables setted")

        (lv, rv) = self._robot.distance()
        print("Sensor values obtained")
        d_r = numpy.interp(rv, S_R, D)
        d_l = numpy.interp(lv, S_L, D)
        print("Distances calculated")
        closest_side = "R"
        if d_l < d_r:
            closest_side = "L"
        print("Closest side: {}".format(closest_side))
        if closest_side == "R":
            print("Scanning...")
            while d_l > 15:
                stream.truncate(0)
                camera.capture(stream, format='bgr')
                image = stream.array
                found, x, y, w, h = Candle.position(image)
                if found:
                    robot.motors(0, 0)
                    print("Candle found!!")
                    return RobotStatus.FIRE_ROOM
                robot.motors(-40, 40)
                time.sleep(0.2)
            print("No candle found")
        else:
            print("Scanning...")
            while d_r > 15:
                stream.truncate(0)
                camera.capture(stream, format='bgr')
                image = stream.array
                found, x, y, w, h = Candle.position(image)
                if found:
                    print("Candle found!!")
                    robot.motors(0, 0)
                    return RobotStatus.FIRE_ROOM
                robot.motors(40, -40)
                time.sleep(0.2)
            print("No candle found")
        return RobotStatus.EMPTY_ROOM
        # TODO Move to the left or right until that side sensor reaches a proximity threshold,
        # then rotate until the candle is being detected (return RobotStatus.FIRE_ROOM) or until the other side sensor,
        # reaches a threshold, then return RobotStatus.EMPTY_ROOM
