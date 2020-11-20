from geekhub.common import MsgType
from .worker import Worker


class CheckWorker(Worker):

    def __init__(self, session_id, interval=0, silent=False):
        super(CheckWorker, self).__init__(session_id, interval, silent)

    def work(self):
        score = self.robot.check_in()
        self.msg_trigger.emit({"msg": score, "type": MsgType.USER_SCORE, "silent": self.silent})