import time
import Candle
from robot_utils.RobotMain import RobotStatus
from robot_utils.WallAvoider import WallAvoider

APPROX_RATIO = 0.6
DEVIATION_OFFSET = - (720 * APPROX_RATIO / 3)


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
        robot = self._robot

        self._align_with_candle()
        self._move_towards_the_candle()

        while self._candle_is_on():
            robot.fan(200)
            time.sleep(0.1)
        time.sleep(1.0)
        robot.fan(0)

    def evaluate_room(self):
        robot = self._robot

        distances = self._calculate_distances()
        farthest_side = RobotSide.Right
        if distances[RobotSide.Left] > distances[RobotSide.Right]:
            farthest_side = RobotSide.Left

        while distances[farthest_side] > 15:
            found, x, y, w, h = self._get_candle_data()
            if found:
                robot.motors(0, 0)
                print("Candle found!!")
                return RobotStatus.FIRE_ROOM
            robot.motors(RobotSide.get_closer_to(farthest_side))

            distances = self._calculate_distances()
            time.sleep(0.2)
        print("No candle found")

        return RobotStatus.EMPTY_ROOM

    def _align_with_candle(self, offset=0):
        robot = self._robot
        converged = False
        while not converged:
            found, x, y, w, h = self._get_candle_data()

            if found:
                xm = x + w / 2
                dx = xm - 360 + offset
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

    def _move_towards_the_candle(self):
        robot = self._robot
        found, x, y, w, h = self._get_candle_data()
        count = 0
        while w < 720 * 0.6:
            if count >= 10:
                count = 0
                self._align_with_candle()

            robot.motors(50, 50)
            time.sleep(0.1)
            found, x, y, w, h = self._get_candle_data()
            count += 1
        self._align_with_candle(DEVIATION_OFFSET)

    def _get_candle_data(self):
        self._stream.truncate(0)
        self._camera.capture(self._stream, format='bgr')
        image = self._stream.array
        return Candle.position(image)

    def _candle_is_on(self):
        self._stream.truncate(0)
        self._camera.capture(self._stream, format='bgr')
        image = self._stream.array
        found, x, y, w, h = Candle.position(image)
        return Candle.state(image, x, y, w, h)

    def _calculate_distances(self):
        (lv, rv) = self._robot.distance()
        while self._robot.error:
            (lv, rv) = self._robot.distance()
        (d_l, d_r) = WallAvoider.interpolate_distances((lv, rv))
        return [d_l, d_r]
