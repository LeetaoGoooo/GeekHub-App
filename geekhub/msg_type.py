from enum import Enum, unique


@unique
class MsgType(Enum):
    USER_INFO = 0
    USER_SCORE = 1
    MSG_NOTIFICATION = 2
    MOLECULES_NOTIFICATION = 3