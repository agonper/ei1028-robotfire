from picamera.array import PiRGBArray
from picamera import PiCamera

from robot_utils.Robot2 import *

from robot_utils.LineDetectorPublisher import LineDetectorPublisher
from robot_utils.RoomController import *
from robot_utils.WallAvoider import WallAvoider

__author__ = 'Alberto'

TIME_BETWEEN_NOTIFICATIONS = 2.0
BEHAVIOR = "Simple"

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
        while True:
            if self._status == RobotStatus.START_ROOM:
                self._wall_avoider.move_without_crashing()
            if self._status == RobotStatus.PASSAGE:
                self._wall_avoider.move_without_crashing()
            if self._status == RobotStatus.UNEVALUATED_ROOM:
                self._step_inside_room()
                self._status = self._room_controller.evaluate_room()
            if self._status == RobotStatus.EMPTY_ROOM:
                self._wall_avoider.move_without_crashing()
            if self._status == RobotStatus.FIRE_ROOM:
                self._room_controller.extinguish_fire()
                if BEHAVIOR == "Simple":
                    print("Finishing run loop")
                    break
                self._status = RobotStatus.EMPTY_ROOM
            time.sleep(0.2)

    def notify(self, value):
        now = time.time()
        if now - self._last_notified > TIME_BETWEEN_NOTIFICATIONS:
            self._last_notified = now
            self._status = RobotStatus.next_status(self._status)
            print("Nuevo estado {}".format(self._status))

    def set_publisher(self, publisher):
        self._publisher = publisher

    def _step_inside_room(self):
        for _ in range(12):
            self._wall_avoider.move_without_crashing()
            time.sleep(0.1)

def main():
    agent_robot = Robot(ULTRASONIC_CONFIG)
    kill_signal = threading.Event()

    camera = PiCamera()
    room_controller = RoomController(agent_robot, camera=camera, stream=PiRGBArray(camera))
    wall_avoider = WallAvoider(agent_robot, kill_signal=kill_signal)
    light_detector = LineDetectorPublisher(agent_robot, kill_signal=kill_signal)
    light_detector.daemon = True

    try:
        brain_robot = RobotMain(robot=agent_robot, wall_avoider=wall_avoider, room_controller=room_controller)
        light_detector.subscribe(brain_robot)
        light_detector.start_detecting()
        brain_robot.run()
    except:
        print("Exception")
    finally:
        kill_signal.set()
        agent_robot.terminate()
        camera.close()
        print("END")

if __name__ == '__main__':
    main()
