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
from common.settings import Settings
from common.recorder import Recorder
from common.mods import Mods
from common.base_test_case import BaseTestCase


class TestRecorder(BaseTestCase):
    test_mod = Mods.Recorder

    @classmethod
    def setUpClass(cls):
        """wifi 开启与否不影响测试"""
        super(TestRecorder, cls).setUpClass()
        cls.mod = Recorder(cls.c.device, cls.test_mod)
        cls.set = Settings(cls.mod.device, "Settings")

    def testStability(self):
        self.case_record_audio(int(self.dicttesttimes.get("RECORDER".lower())))

    def case_record_audio(self, times):
        self.mod.logger.debug("Do Record Audio test " + str(times) + ' Times')
        self.mod.enter()
        self.mod.delete_all_audio()
        for loop in range(times):
            try:
                name = self.mod.random_name(loop)
                if self.mod.record(name) and \
                        self.mod.play(name) and \
                        self.mod.delete(name):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.save_fail_img()
                self.mod.logger.warning(traceback.format_exc())
                self.mod.back_to_home()
                self.mod.enter()
        self.mod.delete_all_audios()
        self.mod.back_to_home()
        self.mod.logger.debug('record audio Test complete')


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestRecorder)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
