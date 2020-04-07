#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import unittest

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)

from common.gmail import Gmail
from common.interrupt import GoogleMapsInterrupt
from common.settings import Settings
from common.message import Message
from common.contacts import Contacts
from common.camera import Camera
from common.gallery_tcl import Gallery
from common.recorder import Recorder
from common.google_music import google_Music
from common.yt_music import YTMusic
from common.native_music import native_Music
from common.chrome import Chrome
from common.browser import Browser
from common.schedule import Schedule
import traceback

mod = ""


class PreSetUp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.serino_m = device_id
        # serino_m = utils.get_m_device()
        # serino_s = utils.get_s_device()
        cls.mod = Settings(cls.serino_m, "settings")
        global mod
        mod = cls.mod

        cls.device = cls.mod.device
        # cls.setup_wiz = SetupWiz(cls.device, 'setup wiz')
        cls.contacts = Contacts(cls.device, 'contacts')
        cls.settings = Settings(cls.device, 'settings')
        cls.camera = Camera(cls.device, 'camera')
        cls.message = Message(cls.device, "messages")
        cls.recorder = Recorder(cls.device, 'recorder')
        cls.gallery = Gallery(cls.device, 'gallery')
        #通过adb shell getprop ro.product.name获取项目名并在commom.ini文件中匹配相关参数
        if cls.mod.isMILAN_GL:
            cls.music = native_Music(cls.mod.device, "native_Music")
        elif cls.mod.isMILAN_EEA:
            cls.music = YTMusic(cls.mod.device, "YT-music")
        else:
            cls.music = google_Music (cls.mod.device, "google_Music")
        cls.chrome = Chrome(cls.device, 'chrome')
        cls.browser = Browser(cls.device, 'browser')
        cls.calendar = Schedule(cls.device, 'schedule')
        cls.gmail = Gmail(cls.device, 'gmail')
        cls.maps = GoogleMapsInterrupt(cls.device, 'gmap')

    @classmethod
    def tearDownClass(cls):
        cls.mod.device.watchers.remove()
        cls.mod.back_to_home()

    def test_0_prepare_all_device(self):
        """
        1. 手动执行一次抓图，power+下音量键
        2. 手动添加账号
        3. （可选） 手动拖拽Sound record， Calendar，clock，Gmail，Maps，playMusic，到主屏
        :return:
        """
        self.device.orientation = 'n'
        self.mod.set_screen_off_timeout()
        self.mod.wakeup()
        self.mod.set_screenlock_none()
        self.mod.disable_google_sync()
        self.mod.setup()# push StabilityResource to /sdcard
        self.setup_other_apps()
        self.execute_setup("self.contacts.setup",self.serino_m)
        self.execute_setup("self.camera.setup")
        self.execute_setup("self.message.setup")
        self.execute_setup("self.recorder.setup")
        self.execute_setup("self.gallery.setup")
        self.execute_setup("self.chrome.setup")
        self.execute_setup("self.calendar.setup")
        self.execute_setup("self.gmail.setup")
        self.execute_setup("self.maps.setup")
        self.execute_setup("self.music.setup")
        self.execute_setup("self.browser.setup")

    def execute_setup(self, fun, device_id=""):
        try:
            eval(fun)(device_id) if device_id else eval(fun)()
        except:
            self.mod.save_fail_img()
            self.mod.logger.warning(traceback.format_exc())

    def setup_other_apps(self):
        """
        setup other apps, operation easy
        :return:
        """
        from collections import OrderedDict
        app_list = OrderedDict([('Smart Manager', self.close_guide),
                                ('Switch Phone', self.click_agree),
                                ('File Manager', self.allow_permissions),
                                ('Music',self.mod.allow_permissions),
                                ('Video',self.allow_permissions)])
        for app, action in app_list.items():
            self.mod.start_app(app,b_desk=False)
            self.device.delay()
            action()
            self.mod.back_to_home()
    def close_guide(self):
        if self.device(resourceId="com.tct.onetouchbooster:id/guide_close").exists:
            self.device (resourceId="com.tct.onetouchbooster:id/guide_close").click()
    def click_point(self):
        x, y = 941, 1005
        self.device.click(x, y)

    def allow_permissions(self):
        self.device.delay(10)
        self.click_cancel_if_exists()
        self.mod.allow_permissions()

    def click_cancel_if_exists(self):
        if self.device(text="App optimization").wait.exists(timeout=3000):
            if self.device(resourceId="com.tct.onetouchbooster:id/apop_dialog_checkbox").exists:
                self.device(resourceId="com.tct.onetouchbooster:id/apop_dialog_checkbox").click()
                self.device.delay(1)
            if self.device(text="CANCEL").exists:
                self.device(text="CANCEL").click()
                self.device.delay(1)

    def click_agree(self):
        el = self.device(text="AGREE")
        if el.wait.exists(timeout=2000):
            el.click()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print sys.argv
        print "please input a device id"
    else:
        device_id = sys.argv[1]
        device_id = "VKRST4ORPFD6HMCQ"
        suiteCase = unittest.TestLoader().loadTestsFromTestCase(PreSetUp)
        suite = unittest.TestSuite([suiteCase])
        unittest.TextTestRunner(verbosity=2).run(suite)
        print "--------------------------    FINISH!!!    ---------------------------------------------"
