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
from common.mods import Mods
from common.base_test_case import BaseTestCase


class TestGoogleMapsInterrupt(BaseTestCase):
    test_mod = Mods.Maps

    @classmethod
    def setUpClass(cls):
        """必须开启翻墙翻墙wifi"""
        super(TestGoogleMapsInterrupt, cls).setUpClass()
        cls.mod = GoogleMapsInterrupt(cls.c.device, cls.test_mod)
        cls.wifi = Wifi(cls.mod.device, "task_Wifi")
        cls.mod.back_to_home()
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")

    def testStability(self):
        self.case_maps_interrupt(int(self.dicttesttimes.get('GoogleMap'.lower())))

    def case_maps_interrupt(self, times=1):
        """answer call during maps navigation, check navigation、answer、back navigation results
        """
        self.mod.logger.info("Test GoogleMaps Interrupt %d times." % times)

        self.mod.gps.enter()
        self.mod.gps.switch('On')
        # self.mod.open_location()
        for loop in range(5):
            if self.mod.enter():
                break
        for loop in range(times):
            try:
                # if self.mod.maps_navigation() and self.mod.answer_navigation() and self.mod.back_navigation():
                self.mod.enter()
                if self.mod.maps_navigation():
                    self.trace_success()
                else:
                    self.trace_fail()
                    self.mod.exception_end_call()
            except:
                self.logger.warning(traceback.format_exc())
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
