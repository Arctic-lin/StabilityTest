#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest



lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not lib_path in sys.path:
    sys.path.append(lib_path)
from common.settings import Wifi
from common.base_test_case import BaseTestCase
from common.mods import Mods

class TestWifi(BaseTestCase):
    test_mod = Mods.Wifi

    @classmethod
    def setUpClass(cls):
        super(TestWifi, cls).setUpClass()
        cls.mod = Wifi(cls.c.device, cls.test_mod)
        cls.ssid = cls.mod.config.getstr("wifi_name", "Wifi", "common")
        cls.pwd = cls.mod.config.getstr("wifi_password", "Wifi", "common")
        cls.security = cls.mod.config.getstr("wifi_security", "Wifi", "common")
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")

    def testSwitchWifi(self):
        self.case_switch(self.ssid, self.pwd, self.security,
                         int(self.dicttesttimes.get("SwitchTimes".lower(), 0)))

    def testConnectWifi(self):
        self.case_connect(self.ssid, self.pwd, self.security,
                          int(self.dicttesttimes.get("ConnectTimes".lower(), 0)))

    def case_connect(self, ssid, pwd, security, times=1):
        '''case:connect wifi in wifi settings
        '''
        self.mod.logger.debug("Dis/Connect Wifi %s Times." % times)
        self.mod.enter()
        self.mod._connect(ssid, pwd, security)
        for loop in range(times):
            try:
                if self.mod.open_close_wifi():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.back_to_home()
            finally:
                self.mod.back_to_wifi()
        # self.mod.forget(ssid)
        self.mod.close()
        self.mod.back_to_home()
        self.mod.logger.debug("Wifi Connect And Disconnect Test Mission Complete")

    def case_switch(self, ssid, pwd, security, times=1):
        '''case:switch wifi in quick settings panel
         arg: suc_times -- success times
        '''
        self.mod.logger.debug("Wifi switch %s Times." % times)
        self.mod.enter()
        self.mod._connect(ssid, pwd, security)
        self.mod.close()
        self.mod.back_to_home()
        for loop in range(times):
            try:
                if self.mod.open_quick_wifi(ssid) and self.mod.web_refresh() and self.mod.close_quick_wifi(ssid):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.device.press.home()
        self.mod.enter()
        # self.mod.open()
        # self.mod.forget(ssid)
        self.mod.close()
        self.mod.back_to_home()
        self.mod.logger.debug("Wifi Switch Test Mission Complete")


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestWifi)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
