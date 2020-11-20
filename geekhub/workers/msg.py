from geekhub.common import MsgType
from .worker import Worker


class MsgWorker(Worker):
    """
        获取消息的线程：
            1.  消息
            2.  分子
            3.  主题 TODO
            4.  用户 TODO
    """

    def __init__(self, session_id, interval=0, silent=False):
        super(MsgWorker, self).__init__(session_id, interval, silent)

    def work(self):
        msg_count, molecules_count = self.robot.get_msg()
        self.msg_trigger.emit({"msg": msg_count, "type": MsgType.MSG_NOTIFICATION, "silent": self.silent})
        self.msg_trigger.emit({"msg": molecules_count, "type": MsgType.MOLECULES_NOTIFICATION, "silent": self.silent})
