#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2019/7/25 11:35

information about this file
"""

from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.settings import GPS
from common.settings import NFC
from common.settings import Bt
from common.settings import Airplane
from common.statusbar import StatusBar
from common.base_test_case import BaseTestCase
from common.mods import Mods

class SettingsStatusbar(BaseTestCase):
    test_mod = Mods.Gps

    @classmethod
    def setUpClass(cls):
        super(SettingsStatusbar, cls).setUpClass()
        # init multi instance
        cls.mod = GPS(cls.c.device, cls.test_mod)
        cls.mod_nfc = NFC(cls.c.device, Mods.Gps)
        cls.mod_bt = Bt(cls.c.device, Mods.Bt)
        cls.mod_air = Airplane(cls.c.device, Mods.Airplane)
        cls.bar = StatusBar(cls.c.device, Mods.statusbar)

        cls.carrier_service_num = cls.mod.get_carrier_service_num()

        # init watchers
        cls.mod.device.watcher("LOCATION").when(textContains="No location access").when(text="CLOSE").click(
            text="CLOSE")
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")

    # @unittest.skip("skip for debug")
    def test_gps(self):
        """
        ENDURANCE_GPS_ONOFF_001 GPS 开关 1(setting) 20
        ENDURANCE_GPS_ONOFF_002 GPS 开关 2 (面板)   20
        :return:
        """
        self.case_set_gps(int(self.dicttesttimes.get("gps_in_set".lower())))
        self.case_bar_gps(int(self.dicttesttimes.get("gps_in_status".lower())))

        self.mod.enable_gps()

    # @unittest.skip("skip for debug")
    def test_airplane(self):
        """
        ENDURANCE_AIRPLANE_ONOFF_001    Flight Mode开关测试 (Setting)   20
        ENDURANCE_AIRPLANE_ONOFF_002    Flight Mode开关测试 (面板)        20
        :return:
        """
        self.case_set_air(int(self.dicttesttimes.get("ap_in_set".lower())))
        self.case_bar_air(int(self.dicttesttimes.get("ap_in_status".lower())))
        self.mod_air.disable_airplane()

    # @unittest.skip("skip for debug")
    def test_nfc(self):
        """
        ENDURANCE_NFC_ONOFF_001 NFC开关测试 (Setting)       20
        ENDURANCE_NFC_ONOFF_002 NFC开关测试 (面板)          20
        :return:
        """

        self.case_set_nfc(int(self.dicttesttimes.get("nfc_in_set".lower())))
        self.case_bar_nfc(int(self.dicttesttimes.get("nfc_in_status".lower())))

    # @unittest.skip("skip for debug")
    def test_bt(self):
        """
        ENDURANCE_BT_ONOFF_00   1BT 开关测试1 (Settings)  20
        ENDURANCE_BT_ONOFF_002  BT 开关测试2 (面板)       20
        :return:
        """
        self.case_set_bt(int(self.dicttesttimes.get("bt_in_set".lower())))
        self.case_bar_bt(int(self.dicttesttimes.get("bt_in_status".lower())))

    def case_set_gps(self, times=1):
        self.mod.logger.info("switch gps %d times in setting" % times)
        self.mod.enter()
        self.mod.switch("Off")
        for loop in range(times):
            try:
                if self.mod.switch("On") and self.mod.switch("Off"):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("switch gps %d times in setting completed" % times)

    def case_bar_gps(self, times=1):
        self.mod.logger.info("switch gps %d times in status bar completed" % times)
        self.mod.device.open.quick_settings()
        # self.bar.device(resourceId="com.android.systemui:id/tile_page").scroll.horiz.to(text="Location")
        self.bar.switch_gps("Off")
        for loop in range(times):
            try:
                if self.bar.switch_gps("On") and self.bar.switch_gps("Off"):
                    self.trace_success()
            except Exception, e:
                self.mod.logger.info(e)
                self.mod.save_fail_img()
        self.bar.switch_gps("On")       # 切换回GPS on防止map case有问题
        self.mod.back_to_home()
        self.mod.logger.info("switch gps %d times in status bar completed" % times)

    def case_set_nfc(self, times=1):
        self.mod_nfc.logger.info("switch NFC %d times in setting" % times)
        if self.mod_nfc.enter():
            self.mod_nfc.switch("OFF")
            for loop in range(times):
                try:
                    if self.mod_nfc.switch("ON") and self.mod_nfc.switch("OFF"):
                        self.trace_success()
                except:
                    self.mod_nfc.logger.error(traceback.format_exc())
                    self.mod_nfc.save_fail_img()
            self.mod_nfc.back_to_home()
            self.mod_nfc.logger.info("switch NFC %d times in setting completed" % times)
        else:
            self.mod_nfc.logger.info ("NFC Not Support")
            self.trace_success ()
    def case_bar_nfc(self, times=1):
        self.mod_nfc.logger.info("switch nfc %d times in status bar completed" % times)
        if self.mod_nfc.enter ():
            self.mod_nfc.device.open.quick_settings()
            self.bar.switch_nfc("Off")
            for loop in range(times):
                try:
                    if self.bar.switch_nfc("On") and self.bar.switch_nfc("Off"):
                        self.trace_success()
                except:
                    self.mod_nfc.logger.error(traceback.format_exc())
                    self.mod_nfc.save_fail_img()
            self.mod_nfc.back_to_home()
            self.mod_nfc.logger.info("switch nfc %d times in status bar completed" % times)
        else:
            self.mod_nfc.logger.info ("NFC Not Support")
            self.trace_success ()

    def case_set_bt(self, times=1):
        self.mod_bt.logger.info("switch BT %d times in setting" % times)
        self.mod_bt.enter()
        self.mod_bt.switch("OFF")
        for loop in range(times):
            try:
                if self.mod_bt.switch("ON") and self.mod_bt.switch("OFF"):
                    self.trace_success()
            except:
                self.mod_bt.logger.error(traceback.format_exc())
                self.mod_bt.save_fail_img()
        self.mod_bt.back_to_home()
        self.mod_bt.logger.info("switch BT %d times in setting completed" % times)

    def case_bar_bt(self, times=1):
        self.mod_bt.logger.info("switch bt %d times in status bar completed" % times)
        self.mod_bt.device.open.quick_settings()
        self.bar.switch_bt("Off")
        for loop in range(times):
            try:
                if self.bar.switch_bt("On") and self.bar.switch_bt("Off"):
                    self.trace_success()
            except:
                self.mod_bt.logger.error(traceback.format_exc())
                self.mod_bt.save_fail_img()
        self.mod_bt.back_to_home()
        self.mod_bt.logger.info("switch bt %d times in status bar completed" % times)

    def case_set_air(self, times=1):
        self.mod_air.logger.info("switch airplane %d times in setting" % times)
        self.mod_air.enter()
        self.mod_air.switch("OFF")
        for loop in range(times):
            try:
                if self.mod_air.switch("ON") and self.mod_air.switch("OFF"):
                    self.trace_success()
            except:
                self.mod_air.logger.error(traceback.format_exc())
                self.mod_air.save_fail_img()
        self.mod_air.back_to_home()
        self.mod_air.logger.info("switch airplane %d times in setting completed" % times)

    def case_bar_air(self, times=1):
        self.mod_air.logger.info("switch airplane %d times in status bar completed" % times)
        self.mod_air.device.open.quick_settings()
        self.bar.switch_airplane("Off")
        for loop in range(times):
            try:
                if self.bar.switch_airplane("On") and self.bar.switch_airplane("Off"):
                    self.trace_success()
            except:
                self.mod_air.logger.error(traceback.format_exc())
                self.mod_air.save_fail_img()
        self.mod_air.back_to_home()
        self.mod_air.logger.info("switch airplane %d times in status bar completed" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(SettingsStatusbar)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
