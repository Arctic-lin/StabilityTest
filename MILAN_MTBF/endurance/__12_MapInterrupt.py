#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)
from common.settings import Wifi
from common.interrupt import GoogleMapsInterrupt
from common.settings import GPS


class TestGoogleMapsInterrupt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        serinoM = "MDEVICE"
        serinoS = "SDEVICE"
        # serinoM = "5000000266"
        # serinoS = "5900000037"
        cls.mod = GoogleMapsInterrupt(serinoM, "Maps", serinoS)
        cls.gps = GPS(cls.mod.device, "GPS")
        cls.wifi = Wifi(cls.mod.device, "task_Wifi")
        cls.mod.back_to_home()
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        cls.wifi.connect_wifi(cls.mod.config.getstr("wifi_name", "Wifi", "common"),
                              cls.mod.config.getstr("wifi_password", "Wifi", "common"),
                              cls.mod.config.getstr("wifi_security", "Wifi", "common"))
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")

    @classmethod
    def tearDownClass(cls):
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").remove()
        cls.mod.device.watcher("WIFI_ENCRYPTION").remove()
        cls.wifi.disconnect_wifi(cls.mod.config.getstr("wifi_name", "Wifi", "common"))
        cls.mod.clear_notification()
        cls.mod.logger.debug('GoogleMapsInterrupt Mission Complete.')
        cls.mod.logger.info("Success Times: %s." % cls.mod.suc_times)
        rate = cls.mod.suc_times / cls.mod.test_times * 100
        if rate < 95:
            cls.mod.logger.warning("Result Fail Success Rate Is " + str(rate) + '%')
        else:
            cls.mod.logger.info("Result Pass Success Rate Is " + str(rate) + '%')
        # cls.mod.charging_full(critical=20)

    def setUp(self):
        self.mod.back_to_home()
        # self.mod.logger.info("battery capacity: %s" % self.mod.adb.shell("cat sys/class/power_supply/battery/capacity"))
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def tearDown(self):
        self.mod.back_to_home()
        # self.mod.logger.info("battery capacity: %s" % self.mod.adb.shell("cat sys/class/power_supply/battery/capacity"))
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def testStability(self):
        self.case_maps_interrupt(int(self.mod.dicttesttimes.get('GoogleMap'.lower())))

    def case_maps_interrupt(self, times=1):
        """answer call during maps navigation, check navigation、answer、back navigation results
        """
        self.mod.logger.info("Test GoogleMaps Interrupt %d times." % times)
        self.gps.enter()
        self.gps.switch("ON")
        self.mod.enter()
        for loop in range(times):
            try:
                self.mod.enter()
                if self.mod.maps_navigation() and self.mod.answer_navigation() and self.mod.back_navigation():
                    self.mod.suc_times += 1
                    self.mod.logger.info("Trace Success Loop " + str(loop + 1))
                else:
                    self.mod.exception_end_call()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exception_end_call()
            finally:
                self.mod.back_to_home()

        # self.mod.close_location()
        self.mod.logger.info("Test GoogleMaps Interrupt %d times complete." % times)


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestGoogleMapsInterrupt)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
