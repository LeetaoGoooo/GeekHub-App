from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import threading
from robot import Robot
import json
from pathlib import Path
import sys


class GeekHubSystemTray(QSystemTrayIcon):

    def __init__(self, *args, **kwargs):
        super(GeekHubSystemTray, self).__init__(*args, **kwargs)
        self.setIcon(QIcon('geekhub.ico'))
        self.geek_hub = None
        self.molecules_timer = None
        self.check_in_timer = None
        self.msg_timer = None
        self.setting_config = {}
        self.load_settings()

    def init_menu(self):
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
        self.msg_notification_action = QAction("消息提醒", self, triggered=self.msg_notification)
        self.msg_notification_action.setCheckable(True)
        self.msg_notification_action.setChecked(self.setting_config.get("msg", False))
        self.refresh_action = QAction("刷新", self, triggered=self.refresh)
        self.quit_action = QAction("退出", self, triggered=self.quit)
        self.menu.addActions(
            [self.user_info_action, self.user_score_action, self.setting_action, self.auto_check_action,
             self.molecules_notification_action, self.msg_notification_action, self.refresh_action, self.quit_action])
        self.setContextMenu(self.menu)

    def init_app(self):
        self.geek_hub = Robot(self.setting_config.get("session"))
        self.get_user_info()
        self.check_in(silent=True)
        if self.setting_config.get("msg"):
            self.msg_timer = IntervalThread(func=self.get_msg, interval=10 * 60)
            self.msg_timer.start()
        if self.setting_config.get("molecule") and self.msg_timer is None:
            self.molecules_timer = IntervalThread(func=self.get_msg, interval=10 * 60)
            self.molecules_timer.start()
        if self.setting_config.get("check"):
            self.check_in_timer = IntervalThread(func=self.check_in, interval=10 * 60)
            self.check_in_timer.start()

    def get_user_info(self):
        print("get user info")
        if self.geek_hub is None:
            self.geek_hub = Robot(self.setting_config.get("session"))
        user_name = self.geek_hub.get_user_info()
        if user_name:
            self.user_info_action.setText(f'用户名:{user_name}')
        else:
            QMessageBox.warning(None, "警告", "session过期或获取用户名失败", QMessageBox.Yes)

    def check_in(self, silent=False):
        print('check in')
        if self.geek_hub is None:
            self.geek_hub = Robot(self.setting_config.get("session"))
        score = self.geek_hub.check_in()
        if isinstance(score, int):
            self.user_score_action.setText(f'积分:{score}')
            if not silent:
                QMessageBox.information(None, '签到', f'签到成功,当前积分{score}', QMessageBox.Yes)
        else:
            QMessageBox.warning(None, "警告", "session过期或获取用户名失败", QMessageBox.Yes)

    def get_msg(self):
        if self.geek_hub is None:
            self.geek_hub = Robot(self.setting_config.get("session"))
        msg_count, molecules_count = self.geek_hub.get_msg()
        if self.setting_config.get("msg", False):
            if msg_count is not None and int(msg_count) > 0:
                QMessageBox.information(None, '消息', f'你有{msg_count}条新的消息待查看!', QMessageBox.Yes)

        if self.setting_config.get("molecule", False):
            if molecules_count is not None and int(molecules_count) > 0:
                QMessageBox.information(None, '分子', '有新的分子待参加', QMessageBox.Yes)

    def preferences(self):
        session, ok_pressed = QInputDialog.getText(None, "设置", "输入你的Session Id", QLineEdit.Normal, "")
        if ok_pressed:
            if session.strip():
                self.setting_config['session'] = session
                self.save_settings()
                self.init_app()
            else:
                QMessageBox.warning(None, "警告", "Session id 格式有误!", QMessageBox.Yes)

    def auto_check_in(self, state):
        if not self.setting_config.get("session", False):
            QMessageBox.warning(None, '警告', '请先设置 Session！', QMessageBox.Yes)
            self.auto_check_action.setChecked(False)
            return

        if state:
            self.setting_config['check'] = state
            self.save_settings()
            self.check_in()
            self.check_in_timer = IntervalThread(func=self.check_in, interval=12 * 3600)
            self.check_in_timer.start()
        else:
            if self.check_in_timer is not None and self.check_in_timer.isRunning():
                self.check_in_timer.stop()
            self.check_in_timer = None

    def msg_notification(self, state):
        if not self.setting_config.get("session", False):
            QMessageBox.warning(None, '警告', '请先设置 Session！', QMessageBox.Yes)
            self.msg_notification_action.setChecked(False)
            return
        if state:
            self.setting_config['msg'] = state
            self.save_settings()
            self.get_msg()
            if self.molecules_timer is None:
                self.msg_timer = IntervalThread(func=self.get_msg, interval=10 * 60)
                self.msg_timer.start()
        else:
            if self.msg_timer is not None and self.msg_timer.isRunning():
                self.msg_timer.stop()
            self.msg_timer = None

    def molecules_notification(self, state):
        """
        推送内容包含 molecule 关键词
        :param sender:
        :return:
        """
        if not self.setting_config.get("session", False):
            QMessageBox.warning(None, '警告', '请先设置 Session！', QMessageBox.Yes)
            self.molecules_notification_action.setChecked(False)
            return
        if state:
            self.setting_config['molecule'] = state
            self.save_settings()
            self.get_msg()
            if self.msg_timer is None:
                self.molecules_timer = IntervalThread(func=self.get_msg, interval=10 * 60)
                self.molecules_timer.start()
        else:
            if self.molecules_timer is not None and self.molecules_timer.isRunning():
                self.molecules_timer.stop()
            self.molecules_timer = None

    def refresh(self):
        IntervalThread(func=self._update, interval=0).start()

    def _update(self):
        self.check_in(silent=True)
        self.get_user_info()
        self.get_msg()

    def quit(self):
        self.setVisible(False)
        sys.exit()

    def save_settings(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.setting_config, f)

    def load_settings(self):
        if Path('config.json').exists():
            with open('config.json', 'r', encoding='utf-8') as f:
                self.setting_config = json.load(f)
            self.init_menu()
            self.init_app()
        else:
            self.init_menu()


class IntervalThread(threading.Thread):
    def __init__(self, func=None, interval=None):
        super(IntervalThread, self).__init__()
        self.interval = interval
        self.func = func
        self.stopped = False

    def run(self):
        if self.interval:
            while not self.stopped:
                self.func()
                self.sleep(self.interval)
        else:
            self.func()

    def stop(self):
        self.stopped = False

    def restart(self):
        self.stopped = True
        self.start()


if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    tray = GeekHubSystemTray()
    tray.show()
    app.exec_()
