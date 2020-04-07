# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.settings import Bt
from common.statusbar import StatusBar
from common.base_test_case import BaseTestCase
from common.mods import Mods

class BtEndurance(BaseTestCase):

    test_mod = Mods.Bt
    @classmethod
    def setUpClass(cls):
        super(BtEndurance, cls).setUpClass()
        cls.mod = Bt(cls.c.device, cls.test_mod)
        cls.bar = StatusBar(cls.c.device, "statusbar")
        cls.carrier_service_num = cls.mod.get_carrier_service_num()

    @classmethod
    def tearDownClass(cls):
        super(BtEndurance, cls).tearDownClass()

    def testEndurance(self):
        """
        ENDURANCE_BT_ONOFF_00   1BT 开关测试1 (Settings)  20
        ENDURANCE_BT_ONOFF_002  BT 开关测试2 (面板)       20
        :return:
        """
        self.case_set_bt(int(self.dicttesttimes.get("bt_in_set".lower())))
        self.case_bar_bt(int(self.dicttesttimes.get("bt_in_status".lower())))

    def case_set_bt(self, times=1):
        self.mod.logger.info("switch BT %d times in setting" % times)
        self.mod.enter()
        self.mod.switch("OFF")
        for loop in range(times):
            try:
                if self.mod.switch("ON") and self.mod.switch("OFF"):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("switch BT %d times in setting completed" % times)

    def case_bar_bt(self, times=1):
        self.mod.logger.info("switch bt %d times in status bar completed" % times)
        self.mod.device.open.quick_settings()
        self.bar.switch_bt("Off")
        for loop in range(times):
            try:
                if self.bar.switch_bt("On") and self.bar.switch_bt("Off"):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("switch bt %d times in status bar completed" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(BtEndurance)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
