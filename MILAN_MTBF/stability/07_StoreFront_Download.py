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
from common.playstore import PlayStore
from common.mods import Mods
from common.base_test_case import BaseTestCase


class TestPlayStore(BaseTestCase):
    test_mod = Mods.Store

    @classmethod
    def setUpClass(cls):
        """必须开启wifi"""
        super(TestPlayStore, cls).setUpClass()
        cls.mod = PlayStore(cls.c.device, cls.test_mod)
        cls.wifi = Wifi(cls.mod.device, "task_Wifi")
        cls.mod.back_to_home()
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        # if cls.mod.config.testtype == "STABILITY":
        cls.wifi.connect_wifi(cls.mod.config.getstr("wifi_name", "Wifi", "common"),
                              cls.mod.config.getstr("wifi_password", "Wifi", "common"),
                              cls.mod.config.getstr("wifi_security", "Wifi", "common"))

        cls.mod.device.watcher("OK").when(text="CHECK FOR UPDATE").when(text='OK').click(text="OK")

    @classmethod
    def tearDownClass(cls):
        cls.mod.device.watcher("WIFI_ENCRYPTION").remove()
        super(TestPlayStore, cls).tearDownClass()

    def testStability(self):
        self.case_open_close(int(self.dicttesttimes.get("OPENCLOSE".lower())))
        self.case_store_download(int(self.dicttesttimes.get("DOWNLOAD".lower())))

    def case_store_front(self, times=1):
        '''case check play store interface
        '''
        self.mod.logger.debug("Check play store interface %d times." % times)
        for loop in range(times):
            try:
                if self.mod.enter() and self.mod.check_interface() and self.mod.exit():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.back_to_home()
        self.mod.device.press.home()
        self.mod.logger.debug('Check play store interface test complete')

    def case_open_close(self, times=1):
        '''case open / close play store
        '''
        self.mod.logger.debug("Open and close play store %d times." % times)
        for loop in range(times):
            try:
                if self.mod.enter() and \
                        self.mod.exit():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exit()
        self.mod.device.press.home()
        self.mod.logger.debug('Open and close play store test complete')

    def case_store_download(self, times=1):
        '''case download TCTTemperature apk in play store
        '''
        # apk_name = 'Google Authenticator'
        apk_name = 'MultiTouch Tester'
        self.mod.logger.debug("Download {} apk {} times.".format(apk_name, times))
        self.mod.enter()
        for loop in range(times):
            try:
                if self.mod.download_open_apk(apk=apk_name) and \
                        self.mod.back_main_app():
                    self.trace_success()
                else:
                    self.mod.back_main_app()
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.back_main_app()
        self.mod.exit()
        self.mod.device.press.home()
        self.mod.logger.debug('Download {} apk test complete'.format(apk_name))


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestPlayStore)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
