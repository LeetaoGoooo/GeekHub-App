import wx
import wx.adv
from robot import Robot
import json
import os
from pathlib import Path
from threading import Thread
import collections
import time


class GeekHubStatusBarApp(wx.adv.TaskBarIcon):

    def __init__(self, icon, title, *args, **kwargs):
        super(GeekHubStatusBarApp, self).__init__(*args, **kwargs)
        self.setIcon(wx.Icon(icon), title)
        self.geek_hub = None
        self.molecules_timer = None
        self.check_in_timer = None
        self.msg_timer = None
        self.setting_config = {}
        self.load_settings()
        self.init()

    def init(self):
        self.init_menu_attrs_list()
        self.init_bind_event()
    
    def init_app(self):
        self.geek_hub = Robot(self.setting_config.get("session"))
        self.get_user_info()
        self.check_in(silent=True)

    def init_menu_attrs_list(self):
        self.user_name_id = wx.NewId()
        self.user_score_id = wx.NewId()
        self.setting_id = wx.NewId()
        self.auto_check_id = wx.NewId()
        self.molecules_notification_id = wx.NewId()
        self.msg_notification_id = wx.NewId()
        self.menu_attrs = [("用户名:?", self.user_name_id), ('积分:?', self.user_score_id),
                           ('设置', self.setting_id), ('自动签到', self.auto_check_id),
                           ('分子提醒', self.molecules_notification_id), ('消息提醒', self.msg_notification_id)]

    def init_bind_event(self):
        self.Bind(wx.EVT_MENU, self.preferences, id = self.setting_id)
        self.Bind(wx.EVT_MENU, self.auto_check_in, id = self.auto_check_id)
        self.Bind(wx.EVT_MENU, self.molecules_notification, id = self.molecules_notification_id)
        self.Bind(wx.EVT_MENU, self.msg_notification, id = self.msg_notification_id)


    def CreatePopupMenu(self):
        menu = wx.Menu()
        for menu_attr in self.menu_attrs:
            menu.Append(*menu_attr[::])
        return menu

    def get_icon(self, name):
        if os.getenv("debug", False):
            return str(f'Resources/{name}.png')
        return str(f'{name}.png')

    def init_menu(self):
        check_in_menu = rumps.MenuItem('自动签到')
        check_in_menu.state = 1 if self.setting_config.get(
            'check', False) else 0
        self.menu.add(check_in_menu)
        msg_menu = rumps.MenuItem("消息提醒")
        msg_menu.state = 1 if self.setting_config.get("msg", False) else 0
        self.menu.add(msg_menu)
        molecules_menu = rumps.MenuItem("分子提醒")
        molecules_menu.state = 1 if self.setting_config.get(
            "molecule", False) else 0
        self.menu.add(molecules_menu)
        if self.setting_config.get("molecule", False) or self.setting_config.get("msg", False):
            self.msg_timer = rumps.Timer(self.get_msg, 10 * 60)
            self.msg_timer.start()

    def get_user_info(self):
        if self.geek_hub is None:
            self.geek_hub = Robot(self.setting_config.get("session"))
        user_name = self.geek_hub.get_user_info()
        if user_name:
            self.user_name_menu.title = user_name
        else:
            rumps.alert("session过期或获取用户名失败", icon_path=self.get_icon('alert'))

    def check_in(self, callback=None, silent=False):
        if self.geek_hub is None:
            self.geek_hub = Robot(self.setting_config.get("session"))
        score = self.geek_hub.check_in()
        if isinstance(score, int):
            self.user_score_menu.title = f'积分:{score}'
            if not silent:
                rumps.notification(
                    "签到", "签到成功!", f"当前积分{score}", icon=self.get_icon('notification'))
        else:
            rumps.alert("获取积分失败,请尝试重新获取", icon_path=self.get_icon('alert'))

    def get_msg(self, callback=None):
        if self.geek_hub is None:
            self.geek_hub = Robot(self.setting_config.get("session"))
        msg_count, molecules_count = self.geek_hub.get_msg()
        if self.setting_config.get("msg", False):
            if msg_count is not None and int(msg_count) > 0:
                rumps.notification(
                    "消息", 'geekhub', f'你有{msg_count}待查看!', icon=self.get_icon('notification'))
        if self.setting_config.get("molecule", False):
            if molecules_count is not None and int(molecules_count) > 0:
                rumps.notification("分子", 'geekhub', f'有新的分子待参加!',
                                   icon=self.get_icon('notification'))


    def preferences(self):
        response = wx.TextEntryDialog(self, '输入的你的Session Id','设置')
        response.SetValue("")
        if response.ShowModal() == wx.ID_OK:
            if response.GetValue().strip():
                session = response.GetValue()
                self.setting_config['session'] = session
                self.save_settings()
                self.init_app()
            else:
                wx.MessageBox('session 值存在问题!', '提示', wx.OK | wx.ICON_INFORMATION)

    def auto_check_in(self, sender):
        state = not sender.state
        if not self.setting_config.get("session", False):
            rumps.alert("请先设置 Session", icon_path=self.get_icon('alert'))
            return
        if state:
            self.setting_config['check'] = state
            self.save_settings()
            self.check_in()
            self.check_in_timer = rumps.Timer(self.check_in, 12 * 3600)
            self.check_in_timer.start()
        else:
            if self.check_in_timer is not None and self.check_in_timer.is_alive():
                self.check_in_timer.stop()
            self.check_in_timer = None
        sender.state = state


    def msg_notification(self, sender):
        state = not sender.state
        if not self.setting_config.get("session", False):
            rumps.alert("请先设置 Session", icon_path=self.get_icon('alert'))
            return
        if state:
            self.setting_config['msg'] = state
            self.save_settings()
            self.get_msg()
            if self.molecules_timer is None:
                self.msg_timer = rumps.Timer(self.get_msg, 10 * 60)
                self.msg_timer.start()
        else:
            if self.msg_timer is not None and self.check_in_timer.is_alive():
                self.msg_timer.stop()
            self.msg_timer = None
        sender.state = state


    def molecules_notification(self, sender):
        """
        推送内容包含 molecule 关键词
        :param sender:
        :return:
        """
        state = not sender.state
        if not self.setting_config.get("session", False):
            rumps.alert("请先设置 Session", icon_path=self.get_icon('alert'))
        if state:
            sender.state = state
            self.setting_config['molecule'] = state
            self.save_settings()
            self.get_msg()
            if self.msg_timer is None:
                self.molecules_timer = rumps.Timer(self.get_msg, 10 * 60)
                self.molecules_timer.start()
        else:
            if self.molecules_timer is not None and self.molecules_timer.is_alive():
                self.molecules_timer.stop()
            self.molecules_timer = None
        sender.state = state

    @rumps.clicked("刷新")
    def update(self, _):
        self.check_in(silent=True)
        self.get_user_info()
        self.get_msg()

    def save_settings(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.setting_config, f)

    def load_settings(self):
        if Path('config.json').exists():
            with open('config.json', 'r', encoding='utf-8') as f:
                self.setting_config = json.load(f)
            self.init_menu()
            self.init_app()


class IntervalThread(Thread):
    def __init__(self, interval=None, func=None):
        assert isinstance(interval, int) and isinstance(
            func, collections.Callable)
        self.interval = interval
        self.func = func
        self.stoped = False

    def run(self):
        while not self.stoped:
            self.func()
            time.sleep(self.interval)

    def stop(self):
        pass


if __name__ == "__main__":
    GeekHubStatusBarApp(icon='logo.icns', title='').run()
