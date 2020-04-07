#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.settings import Wifi
from common.chrome import Chrome
from common.statusbar import StatusBar
from common.mods import Mods
from common.base_test_case import BaseTestCase

class WifiHotspotEndurance(BaseTestCase):
    test_mod = Mods.Wifihotspot

    @classmethod
    def setUpClass(cls):
        super(WifiHotspotEndurance, cls).setUpClass()
        # mdevice = "MDEVICE"
        sdevice = "SDEVICE"
        # sdevice = '9929f085'
        cls.mod = Wifi(cls.c.device, cls.test_mod)
        cls.wifi_s = Wifi(sdevice, "open_wifi")
        cls.browser_s = Chrome(sdevice, "browser_web")
        cls.bar = StatusBar(cls.c.device, "statusbar")
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")

    def setUp(self):
        self.mod.back_to_home()
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def tearDown(self):
        self.mod.back_to_home()
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def xxtest1hotspot_set(self):
        """
        ENDURANCE_WIFI_HOTSPOT_001  WIFI热点(from Setting/下拉Status Bar各50)    100

        :return:
        """
        total_times = int(self.dicttesttimes.get("hotspot_connect_times_set".lower()))
        self.mod.enter_hotspot()
        self.case_wifi_hotspot(int(total_times))

    def test2hotspot_bar(self):
        total_times = int(self.dicttesttimes.get("hotspot_connect_times_bar".lower()))
        self.case_wifi_hospot_bar(total_times)

    def case_wifi_hospot_bar(self, times):
        self.mod.logger.info("wifi hotspot open/close/connect via status bar %d times" % times)
        self.mod.enter_hotspot()
        ssid = self.mod.random_name(8)
        password = self.mod.random_name(8)
        ssid = self.mod.create_wifi_hotspot(ssid, password)
        self.mod.device.delay(2)
        self.mod.device.open.quick_settings()
        for loop in range(times):
            try:
                if ssid and self.bar.switch_hospot('On')\
                        and self.wifi_s._connect(ssid, password, "WPA/WPA2 PSK", enter=True) \
                        and self.wrap_browser_webpage()\
                        and self.bar.switch_hospot('Off'):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.save_fail_img()
                self.mod.logger.warning(traceback.format_exc())
                self.mod.back_to_home()
                self.mod.enter()
            finally:
                self.wifi_s.disable_wifi()
                self.wifi_s.back_to_home()
                # self.mod.close_hotspot()
                self.mod.device.delay()
        self.mod.back_to_home()
        self.mod.logger.info("wifi hotspot open、close、connect via status bar %d times" % times)

    def case_wifi_hotspot(self, times):
        self.mod.logger.info("wifi hotspot open/close/connect %d times" % times)

        for loop in range(times):
            try:
                ssid = self.mod.random_name(loop)
                password = self.mod.random_name(loop)
                ssid = self.mod.create_wifi_hotspot(ssid, password)
                if ssid and self.wifi_s._connect(ssid, password, "WPA/WPA2 PSK", enter=True) and self.wrap_browser_webpage():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.save_fail_img()
                self.mod.logger.warning(traceback.format_exc())
                self.mod.back_to_home()
                self.mod.enter()
            finally:
                self.wifi_s.disable_wifi()
                self.wifi_s.back_to_home()
                self.mod.close_hotspot()
                self.mod.device.delay()
        self.mod.back_to_home()
        self.mod.logger.info("wifi hotspot open、close、connect %d times" % times)

    def wrap_browser_webpage(self):
        self.browser_s.enter()
        return self.browser_s.browser_webpage()


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(WifiHotspotEndurance)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
