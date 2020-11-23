from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from geekhub.common import MsgType
from geekhub.workers import *
import json
from pathlib import Path
import sys


class GeekHubSystemTray(QSystemTrayIcon):

    def __init__(self, *args, **kwargs):
        super(GeekHubSystemTray, self).__init__(*args, **kwargs)
        self.setIcon(QIcon('geekhub.ico'))
        self.check_in_timer = None
        self.msg_timer = None
        self.update = False
        self.setting_config = {}
        self.load_settings()

    def init_menu(self, start=False):
        self.menu = QMenu()
        self.user_info_action = QAction('用户名:?', self)
        self.user_score_action = QAction("积分:?", self)
        self.setting_action = QAction("设置", self, triggered=self.preferences)
        self.auto_check_action = QAction("自动签到", self, triggered=self.auto_check_in)
        self.auto_check_action.setCheckable(True)
        self.auto_check_action.setChecked(self.setting_config.get("check", False))
        self.molecules_notification_action = QAction("分子提醒", self, triggered=self.molecules_notification)
        self.molecules_notification_action.setCheckable(True)
        self.molecules_notification_action.setChecked(self.setting_config.get("molecule", False))
        self.msg_notification_action = QAction("消息提醒", self,
                                               triggered=self.msg_notification)
        self.msg_notification_action.setCheckable(True)
        self.msg_notification_action.setChecked(self.setting_config.get("msg", False))
        self.refresh_action = QAction("刷新", self, triggered=self.refresh)
        self.reward_action = QAction("赞助", self, triggered=self.reward)
        self.quit_action = QAction("退出", self, triggered=self.quit)
        self.menu.addActions(
            [self.user_info_action, self.user_score_action, self.setting_action, self.auto_check_action,
             self.molecules_notification_action, self.msg_notification_action, self.refresh_action, self.quit_action])
        self.setContextMenu(self.menu)
        if start:
            self.init_app()

    def init_app(self):
        self.get_user_info()
        self.check_in(silent=True, interval=0)
        if self.setting_config.get("msg") or self.setting_config.get("molecule"):
            self.msg_timer = MsgWorker(session_id=self.setting_config.get("session", None), interval=10 * 60)
            self.msg_timer.msg_trigger.connect(self.msg_callback)
            self.msg_timer.start()
        if self.setting_config.get("check"):
            self.check_in(silent=False, interval=10 * 60)

    def get_msg(self, silent, interval):
        assert isinstance(silent, bool) and isinstance(interval, int)
        if interval:
            self.msg_timer = MsgWorker(session_id=self.setting_config.get("session", None), interval=10 * 60,
                                       silent=silent)
            self.msg_timer.msg_trigger.connect(self.msg_callback)
            self.msg_timer.start()
        else:
            self.tmp_msg_worker = MsgWorker(session_id=self.setting_config.get("session", None), interval=0,
                                            silent=silent)
            self.tmp_msg_worker.msg_trigger.connect(self.msg_callback)
            self.tmp_msg_worker.start()

    def get_user_info(self):
        self.tmp_user_worker = UserWorker(self.setting_config.get("session"))
        self.tmp_user_worker.msg_trigger.connect(self.msg_callback)
        self.tmp_user_worker.start()

    def check_in(self, silent, interval):
        assert isinstance(silent, bool) and isinstance(interval, int)
        if interval:
            self.check_in_timer = CheckWorker(session_id=self.setting_config.get("session", None), interval=interval,
                                              silent=silent)
            self.check_in_timer.msg_trigger.connect(self.msg_callback)
            self.check_in_timer.start()
        else:
            self.tmp_check_in_worker = CheckWorker(session_id=self.setting_config.get("session", None),
                                                   interval=interval,
                                                   silent=silent)
            self.tmp_check_in_worker.msg_trigger.connect(self.msg_callback)
            self.tmp_check_in_worker.start()

    def preferences(self):
        session, ok_pressed = QInputDialog.getText(None, "设置", "输入你的Session Id", QLineEdit.Normal, "")
        if ok_pressed:
            if session.strip():
                self.setting_config['session'] = session.strip()
                self.save_settings()
                self.init_app()
            else:
                QMessageBox.warning(None, "警告", "Session id 格式有误!", QMessageBox.Yes)

    def auto_check_in(self, state):
        if not self.setting_config.get("session", False):
            QMessageBox.warning(None, '警告', '请先设置 Session！', QMessageBox.Yes)
            self.auto_check_action.setChecked(False)
            return
        else:
            if state:
                self.setting_config['check'] = state
                self.save_settings()
                self.check_in(silent=False, interval=12 * 3600)
            else:
                if self.check_in_timer is not None and self.check_in_timer.isRunning():
                    self.check_in_timer.stop()
                self.check_in_timer = None

    def msg_notification(self, state):
        if not self.setting_config.get("session", False):
            QMessageBox.warning(None, '警告', '请先设置 Session！', QMessageBox.Yes)
            self.msg_notification_action.setChecked(False)
            return
        return self.__notification(state, kind='msg')

    def molecules_notification(self, state):
        if not self.setting_config.get("session", False):
            QMessageBox.warning(None, '警告', '请先设置 Session！', QMessageBox.Yes)
            self.molecules_notification_action.setChecked(False)
            return
        return self.__notification(state, kind='molecules')

    def __notification(self, state, kind='msg'):
        if state:
            self.setting_config[kind] = state
            self.save_settings()
            if self.msg_timer is None:
                self.get_msg(silent=False, interval=10 * 60)
        else:
            if self.msg_timer is not None and self.msg_timer.isRunning() and flag is False:
                self.msg_timer.stop()
                self.msg_timer = None

    def refresh(self):
        if not self.setting_config.get("session", False):
            QMessageBox.warning(None, '警告', '请先设置 Session！', QMessageBox.Yes)
            return
        self.check_in(silent=True, interval=0)
        self.get_user_info()
        self.get_msg(silent=False, interval=0)
        self.update = True

    def quit(self):
        self.setVisible(False)
        sys.exit()

    def reward(self):
        pass

    def save_settings(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.setting_config, f)

    def load_settings(self):
        if Path('config.json').exists():
            with open('config.json', 'r', encoding='utf-8') as f:
                self.setting_config = json.load(f)
            self.init_menu(start=True)
        else:
            self.init_menu()

    def msg_callback(self, resp):
        assert isinstance(resp, dict)
        msg_type = resp.get("type")
        content = resp.get("msg")
        silent = resp.get("silent", False)
        if content is None or content is False:
            QMessageBox.warning(None, "警告", "session过期或获取失败", QMessageBox.Yes)
            return
        if msg_type == MsgType.USER_SCORE:
            self.user_score_action.setText(f'积分:{content}')
            if not silent:
                QMessageBox.information(None, '签到', f'签到成功,当前积分{content}', QMessageBox.Yes)
        elif msg_type == MsgType.USER_INFO:
            self.user_info_action.setText(f'用户名:{content}')
        elif msg_type == MsgType.MSG_NOTIFICATION:
            if (self.setting_config.get("molecule") or self.update) and msg is not None and int(content) > 0:
                QMessageBox.information(None, '消息', f'你有{content}条新的消息待查看!', QMessageBox.Yes)
        elif msg_type == MsgType.MOLECULES_NOTIFICATION:
            if (self.setting_config.get("molecule") or self.update) and msg is not None and int(content) > 0:
                QMessageBox.information(None, '分子', '有新的分子待参加', QMessageBox.Yes)
        else:
            QMessageBox.critical(None, "错误", "未知的消息类型!", QMessageBox.Yes)
        self.update = False


if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    tray = GeekHubSystemTray()
    tray.show()
    app.exec_()
