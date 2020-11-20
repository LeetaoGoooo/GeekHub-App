from .worker import Worker
from geekhub.common import MsgType


class UserWorker(Worker):

    def __init__(self, session_id, interval=0, silent=False):
        super(UserWorker, self).__init__(session_id, interval, silent)

    def work(self):
        user_name = self.robot.get_user_info()
        self.msg_trigger.emit({"msg": user_name, "type": MsgType.USER_INFO, "silent": self.silent})
