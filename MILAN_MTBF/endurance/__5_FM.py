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
from common.fm import FM
from common.base_test_case import BaseTestCase
from common.mods import Mods

class FmEndurance(BaseTestCase):
    test_mod = Mods.Fm
    @classmethod
    def setUpClass(cls):
        super(FmEndurance, cls).setUpClass()
        cls.mod = FM(cls.c.device, cls.test_mod)
        cls.carrier_service_num = cls.mod.get_carrier_service_num()

    @classmethod
    def tearDownClass(cls):
        super(FmEndurance, cls).tearDownClass()

    def testEndurance(self):
        """
        ENDURANCE_FM_ONOFF_001      FM 开关测试      20
        ENDURANCE_FM_CHANNEL_001    不断切换频道     20
        ENDURANCE_FM_CHANNEL_002    长时间播放FM     2
        :return:
        """
        self.case_switch_fm(int(self.dicttesttimes.get("switch_fm_times".lower())))
        self.case_switch_channel(int(self.dicttesttimes.get("switch_channel_times".lower())))
        self.case_play_fm(int(self.dicttesttimes.get("play_fm_times".lower())))

    def case_switch_fm(self, times):
        self.mod.logger.info("switch FM %d times" % times)
        self.mod.enter()
        self.mod.switch("Stop")
        for loop in range(times):
            try:
                if self.mod.switch("Play") and self.mod.switch("Stop"):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.exit()
        self.mod.back_to_home()
        self.mod.logger.info("switch FM %d times completed" % times)

    def case_switch_channel(self, times):
        self.mod.logger.info("switch channel during play radio %d times" % times)
        for loop in range(times):
            try:
                if self.mod.switch_channel():
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("switch channel during play radio %d times" % times)

    def case_play_fm(self, times):
        self.mod.logger.info("Play radio 30 min %d times" % times)
        for loop in range(times):
            try:
                if self.mod.play_fm():
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.logger.info("Play radio 30 min %d times success" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(FmEndurance)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
