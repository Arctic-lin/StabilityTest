﻿# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.settings import Airplane
from common.statusbar import StatusBar


class AirplaneEndurance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        serino = "MDEVICE"
        # serino = "5000000266"
        cls.mod = Airplane(serino, "Airplane")
        cls.bar = StatusBar(cls.mod.device, "statusbar")
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")

    @classmethod
    def tearDownClass(cls):
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").remove()
        cls.mod.device.watcher("WIFI_ENCRYPTION").remove()
        cls.mod.logger.debug('Airplane Mission Complete')
        cls.mod.logger.info("Success Times: %s." % cls.mod.suc_times)
        Rate = cls.mod.suc_times / cls.mod.test_times * 100
        if Rate < 95:
            cls.mod.logger.warning("Result Fail Success Rate Is " + str(Rate) + '%')
        else:
            cls.mod.logger.info("Result Pass Success Rate Is " + str(Rate) + '%')

    def setUp(self):
        self.mod.back_to_home()
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def tearDown(self):
        self.mod.back_to_home()
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def testEndurance(self):
        """
        ENDURANCE_AIRPLANE_ONOFF_001    Flight Mode开关测试 (Setting)   100
        ENDURANCE_AIRPLANE_ONOFF_002    Flight Mode开关测试 (面板)        100

        :return:
        """
        self.case_set_air(int(self.mod.dicttesttimes.get("ap_in_set".lower())))
        self.case_bar_air(int(self.mod.dicttesttimes.get("ap_in_status".lower())))

    def case_set_air(self, times=1):
        self.mod.logger.info("switch airplane %d times in setting" % times)
        self.mod.enter()
        self.mod.switch("OFF")
        for loop in range(times):
            try:
                if self.mod.switch("ON") and self.mod.switch("OFF"):
                    self.mod.suc_times += 1
                    self.mod.logger.info("Trace Success Loop %d" % (loop + 1))
            except Exception, e:
                self.mod.logger.info(e)
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("switch airplane %d times in setting completed" % times)

    def case_bar_air(self, times=1):
        self.mod.logger.info("switch airplane %d times in status bar completed" % times)
        self.mod.device.open.quick_settings()
        self.bar.switch_airplane("OFF")
        for loop in range(times):
            try:
                if self.bar.switch_airplane("ON") and self.bar.switch_airplane("OFF"):
                    self.mod.suc_times += 1
                    self.mod.logger.info("Trace Success Loop %d" % (loop + 1))
            except Exception, e:
                self.mod.logger.info(e)
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("switch airplane %d times in status bar completed" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(AirplaneEndurance)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
