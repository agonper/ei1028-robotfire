import threading
import time

from robot_utils.Robot2 import *

from robot_utils.LineDetectorPublisher import LineDetectorPublisher
from robot_utils.RoomController import *
from robot_utils.WallAvoider import WallAvoider

__author__ = 'Alberto'


class RobotStatus:
    START_ROOM = "START_ROOM"
    PASSAGE = "PASSAGE"
    UNEVALUATED_ROOM = "UNEVALUATED_ROOM"
    EMPTY_ROOM = "EMPTY_ROOM"
    FIRE_ROOM = "FIRE_ROOM"

    @staticmethod
    def next_status(status):
        if status != RobotStatus.PASSAGE:
            return RobotStatus.PASSAGE
        if status == RobotStatus.PASSAGE:
            return RobotStatus.UNEVALUATED_ROOM


class RobotMain:
    def __init__(self, robot, wall_avoider, room_controller):
        self._robot = robot
        self._wall_avoider = wall_avoider
        self._room_controller = room_controller
        self._status = RobotStatus.START_ROOM
        self._publisher = None
        self._last_notified = time.time()

    def run(self):
        count = 0
        while True:
            if self._status == RobotStatus.START_ROOM:
                self._wall_avoider.move_without_crashing()
            if self._status == RobotStatus.PASSAGE:
                self._wall_avoider.move_without_crashing()
            if self._status == RobotStatus.UNEVALUATED_ROOM:
                print("Count: {}".format(count))
                if count <= 3:
                    self._wall_avoider.move_without_crashing()
                    count += 1
                else:
                    count = 0
                    self._status = self._room_controller.evaluate_room()
            if self._status == RobotStatus.EMPTY_ROOM:
                self._wall_avoider.move_without_crashing()
            if self._status == RobotStatus.FIRE_ROOM:
                self._room_controller.extinguish_fire()
            time.sleep(0.1)

    def notify(self, value):
        now = time.time()
        if now - self._last_notified > 1.0:
            self._last_notified = now
            self._status = RobotStatus.next_status(self._status)
            print("Nuevo estado {}".format(self._status))

    def set_publisher(self, publisher):
        self._publisher = publisher


def main():
    agent_robot = Robot(ULTRASONIC_CONFIG)
    kill_signal = threading.Event()
    wall_avoider = WallAvoider(agent_robot)
    room_controller = RoomController(agent_robot)
    light_detector = LineDetectorPublisher(agent_robot, kill_signal=kill_signal)

    try:
        brain_robot = RobotMain(robot=agent_robot, wall_avoider=wall_avoider, room_controller=room_controller)
        light_detector.subscribe(brain_robot)
        light_detector.start_detecting()
        brain_robot.run()
    except:
        agent_robot.terminate()
        kill_signal.set()
        room_controller._camera.close()
        print("END")


if __name__ == '__main__':
    main()
