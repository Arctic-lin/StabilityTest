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

from common.navigation import MenuNavigation
from common.mods import Mods
from common.base_test_case import BaseTestCase


class TestMenuNavigation(BaseTestCase):
    test_mod = Mods.Navigation

    @classmethod
    def setUpClass(cls):
        super(TestMenuNavigation, cls).setUpClass()
        cls.mod = MenuNavigation(cls.c.device, cls.test_mod)

    def testStability(self):
        self.case_launcher_navigation(int(self.dicttesttimes.get("launcher_times".lower(), 0)))
        self.case_apps_navigation(int(self.dicttesttimes.get("apps_times".lower(), 0)))

    def case_launcher_navigation(self, times=1):
        self.mod.logger.info("Laucher Navigation %d Times" % times)
        self.mod.clear_background()
        for loop in range(times):
            try:
                if self.mod._launcher_navigation():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.back_to_home()
        self.mod.clear_background()
        self.mod.logger.info("Laucher Navigation %d Times completed" % times)

    def case_apps_navigation(self, times=1):
        self.mod.logger.debug("Apps Navigation %d Times" % times)
        for loop in range(times):
            try:
                if self.mod._apps_navigation():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.back_to_home()
        self.mod.clear_background()
        self.mod.logger.debug("Apps Navigation %d Times" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestMenuNavigation)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
