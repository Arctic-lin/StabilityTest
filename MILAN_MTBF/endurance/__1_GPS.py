# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.settings import GPS
from common.statusbar import StatusBar
from common.base_test_case import BaseTestCase
from common.mods import Mods

class GPSEndurance(BaseTestCase):
    test_mod = Mods.Gps

    @classmethod
    def setUpClass(cls):
        super(GPSEndurance, cls).setUpClass()
        cls.mod = GPS(cls.c.device, cls.test_mod)
        cls.bar = StatusBar(cls.c.device, "statusbar")
        cls.carrier_service_num = cls.mod.get_carrier_service_num()
        cls.mod.device.watcher("LOCATION").when(textContains="No location access").when(text="CLOSE").click(
            text="CLOSE")

    @classmethod
    def tearDownClass(cls):
        super(GPSEndurance, cls).tearDownClass()
        cls.mod.device.watcher("LOCATION").remove()

    def testEndurance(self):
        """
        ENDURANCE_GPS_ONOFF_001 GPS 开关 1(setting) 20
        ENDURANCE_GPS_ONOFF_002 GPS 开关 2 (面板)   20

        :return:
        """
        self.case_set_gps(int(self.dicttesttimes.get("gps_in_set".lower())))
        self.case_bar_gps(int(self.dicttesttimes.get("gps_in_status".lower())))

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
        self.bar.switch_gps("OFF")
        for loop in range(times):
            try:
                if self.bar.switch_gps("ON") and self.bar.switch_gps("OFF"):
                    self.trace_success()
            except Exception, e:
                self.mod.logger.info(e)
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("switch gps %d times in status bar completed" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(GPSEndurance)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
