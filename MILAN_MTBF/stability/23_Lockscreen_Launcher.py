#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2019/7/25 11:36

information about this file
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.screen import LockScreen
from common.base_test_case import BaseTestCase
from common.mods import Mods

class LockScreenStability(BaseTestCase):
    test_mod = Mods.Lockscreen
    @classmethod
    def setUpClass(cls):
        super(LockScreenStability, cls).setUpClass()
        cls.mod = LockScreen(cls.c.device, cls.test_mod)
        cls.carrier_service_num = cls.mod.get_carrier_service_num()


    @classmethod
    def tearDownClass(cls):
        super(LockScreenStability, cls).tearDownClass()

    def test_lock(self):
        """ ENDURANCE_LOCK_SLIDE_001    灭屏、电量、slide解锁	           20
            ENDURANCE_LOCK_PATTERN_001  灭屏、电量、pattern解锁         20
            ENDURANCE_LOCK_PIN_001      新建、修改、删除PIN码解锁       20
            ENDURANCE_LOCK_PIN_002      灭屏、电量、PIN码解锁           20
            ENDURANCE_LOCK_PASSWORD_001 新建、修改、删除Password解锁    20
            ENDURANCE_LOCK_PASSWORD_002 使用Password解锁               20
            ENDURANCE_WALLPAPER_001     更换home screen壁纸            20
        """

        self.case_lock_screen("Swipe", int(self.dicttesttimes.get("SwipeTimes".lower())))
        self.case_lock_screen("PIN", int(self.dicttesttimes.get("PINTimes".lower())))
        self.case_lock_screen("Password", int(self.dicttesttimes.get("PasswordTimes".lower())))
        self.case_lock_screen("Pattern", int(self.dicttesttimes.get("PtnTimes".lower())))
        self.case_switch_wallpaper(int(self.dicttesttimes.get("WallpaperTimes".lower())))

    def case_lock_screen(self, lock_type, times):
        """
        case for lock screen
        :param lock_type: Swipe, PIN, Password
        :param times:
        :return:
        """
        self.mod.logger.info("swipe lock screen %d times" % times)
        password = self.mod.appconfig(lock_type, "LockScreen")
        self.mod.switch_lock_to_lock(lock_type, password)
        for loop in range(times):
            try:
                if self.mod.lock_screen(lock_type, password):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.switch_lock_to_none(lock_type, password)
        self.mod.logger.info("swipe lock screen %d times completed" % times)

    def case_switch_wallpaper(self, times):
        self.mod.logger.info("switch wallpaper %d times" % times)
        for loop in range(times):
            try:
                if self.mod.switch_wallpaper(loop):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.logger.info("switch wallpaper %d times completed" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(LockScreenStability)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
