import threading
import time

__author__ = 'Alberto'


class LineDetectorPublisher:
    def __init__(self, robot, kill_signal):
        self._robot = robot
        self._subscribers = set()
        self._kill_signal = kill_signal
        self._lock = threading.RLock()

    def subscribe(self, subscriber):
        self._subscribers.add(subscriber)
        subscriber.set_publisher(self)

    def unsubscribe(self, subscriber):
        self._subscribers.remove(subscriber)

    def start_detecting(self):
        def detector(that):
            while True:
                if that._kill_signal.is_set():
                    print("killed")
                    break
                light = self._robot.light()
                if light < 480:
                    that._trigger()
                time.sleep(0.1)

        threading.Thread(target=detector, args=(self,)).start()

    def _trigger(self):
        self._lock.acquire()
        subscribers = list(self._subscribers)[:]
        for subscriber in subscribers:
            subscriber.notify("blank_line")
        self._lock.release()
