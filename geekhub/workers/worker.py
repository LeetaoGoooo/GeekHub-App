import abc
from geekhub.api import Robot

from PyQt5.QtCore import QThread, pyqtSignal


class Worker(QThread):
    msg_trigger = pyqtSignal(dict)

    def __init__(self, session_id, interval=0, silent=False):
        super(Worker, self).__init__()
        assert session_id is not None and isinstance(interval, int)
        self.robot = Robot(cookies=session_id)
        self.interval = interval
        self.silent = silent
        self.stopped = False

    def run(self):
        if self.interval:
            while not self.stopped:
                self.sleep(self.interval)
                self.work()
        else:
            self.work()
            self.quit()

    @abc.abstractmethod
    def work(self):
        pass

    def stop(self):
        self.stopped = True
        self.destroyed()
