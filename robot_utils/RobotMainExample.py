import threading
import time
from robot_utils.LineDetectorPublisher import LineDetectorPublisher

__author__ = 'Alberto'


class SubscriberImpl:
    def __init__(self):
        self._publisher = None

    def notify(self, value):
        print(value)
        self._publisher.unsubscribe(self)

    def set_publisher(self, publisher):
        self._publisher = publisher


class RobotMock:
    def __init__(self):
        self._light = 800

    def light(self):
        return self._light

    def set_blank(self):
        self._light = 500


def main():
    robot = RobotMock()
    kill_signal = threading.Event()
    line_detector = LineDetectorPublisher(robot, kill_signal)
    subscriber = SubscriberImpl()

    line_detector.subscribe(subscriber)
    line_detector.start_detecting()
    time.sleep(2)
    robot.set_blank()
    time.sleep(2)
    kill_signal.set()


if __name__ == '__main__':
    main()
