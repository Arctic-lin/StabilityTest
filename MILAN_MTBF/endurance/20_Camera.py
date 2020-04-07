# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.camera import Camera
from common.base_test_case import BaseTestCase
from common.mods import Mods

class CameraEndurance(BaseTestCase):
    test_mod = Mods.Camera
    @classmethod
    def setUpClass(cls):
        super(CameraEndurance, cls).setUpClass()
        cls.mod = Camera(cls.c.device, cls.test_mod)
        cls.carrier_service_num = cls.mod.get_carrier_service_num()

    @classmethod
    def tearDownClass(cls):
        super(CameraEndurance, cls).tearDownClass()

    def test_camera(self):
        """
        ENDURANCE_CAMERA_PHOTO_001      内存剩余不足情况下拍照         100->20
        ENDURANCE_CAMERA_VIDEO_001      内存剩余不足情况下拍摄video    100->20
        ENDURANCE_CAMERA_3RDPARTY_001   相机相关APP中相机的应用       100-->remove this case

        :return:
        """
        self.case_take_photo(int(self.dicttesttimes.get("photo_times".lower())))
        self.case_take_video(int(self.dicttesttimes.get("video_times".lower())))

    def case_take_photo(self, times=1):
        self.mod.logger.info("low storage take photo %d times" % times)
        # self.mod.logger.info("battery capacity: %s" % self.mod.adb.battery_level())
        self.mod.sleep_if_power_low()
        for loop in range(times):
            try:
                self.mod.logger.info("start low storage take photo %d" % loop)
                if self.mod.take_photo_to_low():
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.back_to_home()
        self.mod.back_to_home()
        self.mod.logger.info("low storage take photo %d times completed" % times)
        self.mod.logger.info("battery capacity: %s" % self.mod.adb.battery_level())

    def case_take_video(self, times=1):
        self.mod.logger.info("low storage take video %d times" % times)
        self.mod.sleep_if_power_low()
        for loop in range(times):
            try:
                self.mod.logger.info("start low storage take video %d" % loop)
                if self.mod.take_video_to_low():
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.back_to_home()
        self.mod.back_to_home()
        self.mod.logger.info("low storage take video %d times completed" % times)




if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(CameraEndurance)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
