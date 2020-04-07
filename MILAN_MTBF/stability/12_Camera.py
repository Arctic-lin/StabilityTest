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
from common.camera import Camera
from common.mods import Mods
from common.base_test_case import BaseTestCase
from common.camera import PORTRAIT, PRO, SUPER_NIGHT, AUTO

class TestCamera(BaseTestCase):
    test_mod = Mods.Camera

    @classmethod
    def setUpClass(cls):
        super(TestCamera, cls).setUpClass()
        cls.mod = Camera(cls.c.device, cls.test_mod)
        cls.set = Settings(cls.mod.device, 'Settings')
        cls.mod.clear_background()
        cls.mod.device.watcher("CAMERA_LONG_USED") \
            .when(textStartsWith="Camera has been idle for quite a while") \
            .click(text="CANCEL")
        cls.mod.device.watcher("CAMERA_DISMISS") \
            .when(text="Can't connect to the camera") \
            .when(text="DISMISS") \
            .click(text="DISMISS")

    def testStability(self):
        """
        目前camera在执行过程中每一步操作执行的特别慢，经常出现找元素时间太长，导致camera自动退出
        所以camera的测试大部分操作都是使用坐标实现
        :return:
        """
        # 对camera进行随机配置
        self.mod.camera_random_setting()

        self.case_take_photo(int(self.dicttesttimes.get('PhotoTimes'.lower())))
        self.case_continuous_shooting(int(self.dicttesttimes.get('ContinuousTimes'.lower())))
        self.case_record_video(int(self.dicttesttimes.get('VideoTimes'.lower())))

        self.case_portrait_photo(int(self.dicttesttimes.get('PortraitTimes'.lower())))
        self.case_supernight_photo(int(self.dicttesttimes.get('SupernightTimes'.lower())))
        self.case_pro_photo(int(self.dicttesttimes.get('ProTimes'.lower())))

    def case_portrait_photo(self, times):
        self.mod.logger.debug('take case_portrait_photo test %d times' % times)
        self.case_take_photo(times=times, photo_mode=PORTRAIT)

    def case_supernight_photo(self, times):
        self.mod.logger.debug('take case_supernight_photo test %d times' % times)
        self.case_take_photo(times=times, photo_mode=SUPER_NIGHT)

    def case_pro_photo(self, times):
        self.mod.logger.debug('take case_pro_photo test %d times' % times)
        self.case_take_photo(times=times, photo_mode=PRO)

    def case_take_photo(self, times=1, photo_mode=AUTO):
        '''take photo by using front / back camera
        '''
        self.mod.logger.debug('take photo test %d times' % times)

        for loop in range(times):
            try:
                self.mod.enter()
                if self.mod.take_photo() and \
                    self.mod.click_camera_picker_btn() and \
                        self.mod.take_photo():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.restart_camera()

        self.mod.delete("photo")
        self.mod.back_to_home()
        self.mod.logger.debug('take photo test %d times completed' % times)

    def case_continuous_shooting(self, times=1):
        '''take photo by using front / back camera
        '''
        self.mod.logger.debug('take continuous photo test %d times' % times)

        for loop in range(times):
            try:
                self.mod.enter()
                # self.mod.switch_photo_mode()
                if self.mod.switch_picker('back') and \
                    self.mod.restart_camera() and \
                    self.mod.continuous_shooting() and \
                    self.mod.restart_camera():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.restart_camera()

        self.mod.delete("photo")
        self.mod.back_to_home()
        self.mod.logger.debug('take continuous photo test %d times completed' % times)

    def case_record_video(self, times=1):
        '''record video by using front / back camera
        '''
        self.mod.logger.debug('record video test %d times' % times)

        for loop in range(times):
            try:
                self.mod.enter()
                self.mod.click_video_mode()
                if self.mod.record_video() and \
                    self.mod.play_video() and \
                    self.mod.click_camera_picker_btn() and \
                    self.mod.record_video() and \
                    self.mod.play_video() and \
                    self.mod.click_camera_picker_btn() and \
                    self.mod.restart_camera():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.restart_camera()

        self.mod.delete('video')
        self.mod.back_to_home()
        self.mod.logger.debug('record video test %d times completed' % times)

if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestCamera)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
