# -*- coding: UTF-8 -*-
"""multi tasking library for scripts.
"""

from camera import Camera
from common import *


class MultiTask(Common):
    def start(self):
        """case precondition, start some apps
        """
        self.logger.debug("Start Some activities")
        try:
            self.start_app("Contacts")
            self.start_app("Messages")
            self.start_app("Camera")
            self.start_app("Phone")
            self.start_app('File Manager')
            self.start_app("Browser")
            self.start_app("Settings")
            self.device.press.home()
            self.started_app_packages = ['com.tct.dialer', 'com.google.android.apps.messaging',
                                         'com.tcl.camera', 'com.tct.dialer',
                                         'com.jrdcom.filemanager', 'com.hawk.android.browser', 'com.android.settings',
                                         'com.tcl.android.launcher']  # 增加launcher，有概率切换到拨号，而此时拨打运营商号码超时，自动关闭了

        except:
            self.logger.warning(traceback.format_exc())

    def interaction(self, times=6):
        """switch applications page
        """
        self.logger.debug("switch applications %d times" % times)
        self.device.press.home()
        self.device.delay(2)
        x, y = 812, 2278
        for loop in range(1, times + 1):
            self.device.press.recent()
            self.logger.info("recent pressed")
            self.device.delay(3)
            # self.device.press.recent()
            for i in range(4):
                self.logger.info("swipe - {}".format(i+1))
                self.device.swipe(200, 450, 900, 450, 10)
            self.device.delay(1)
            ##在recent界面做click操作会导致uiautomator进程被杀
            self.logger.info("adb shell input tap 300 500")
            self.adb.shell("input tap 500 800")
            self.device.delay(3)
        self.device.press.home()
        self.logger.debug("switch applications %d times success" % times)
        return True


if __name__ == '__main__':
    a = MultiTask("5900000040", "task")
    for i in range(10):
        a.interaction(6)
        # a.back_end_call()
        # a.device.swipe(660,200,660,2000, 10)
        # a.interaction(6)
