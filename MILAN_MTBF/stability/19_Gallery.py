#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2018/9/11 8:49

information about this file
"""
from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.settings import Settings
from common.camera import Camera
from common.gallery import Gallery
from common.base_test_case import BaseTestCase
from common.mods import Mods

class TestGallery(BaseTestCase):
    test_mod = Mods.Gallery

    @classmethod
    def setUpClass(cls):
        super(TestGallery, cls).setUpClass()
        cls.mod = Camera(cls.c.device, cls.test_mod)
        cls.set = Settings(cls.mod.device, "Settings")
        cls.gallery = Gallery(cls.mod.device, "Gallery")
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")
        cls.mod.clear_background()

    def tearDown(self):
        super(TestGallery, self).tearDown()
        try:
            self.gallery.del_trash()
        except:
            traceback.format_exc()

    def testStability(self):
        self.case_view_pic(int(self.dicttesttimes.get("PicTest".lower())))
        self.case_view_video(int(self.dicttesttimes.get("VideoTest".lower())))

    def case_view_pic(self, times=1):
        '''view pic in gallery
        '''
        try:
            self.mod.logger.debug("view pic in gallery test %d times" % times)
            self.prepare_resource(take_video=False, num=times)
            self.gallery.enter()
            self.gallery.open_file()
            sx, sy, ex, ey = self.gallery.gen_loc_for_swipe(orientation='h', rate_from=0.9, rate_to=0.1)
            ts = int(times / 2)
        except:
            self.mod.save_fail_img()
            self.logger.warning(traceback.format_exc())

        self.perform_steps(ts, self.gallery.swipe_file, sx, sy, ex, ey)
        #  def swipe_file(self, sx, sy, ex, ey, steps=10, video=False)
        self.perform_steps(ts, self.gallery.del_file)

        self.mod.back_to_home()
        self.mod.logger.debug("view pic in gallery test %d times completed" % times)

    def case_view_video(self, times=1):
        self.mod.logger.debug("view video in gallery test %d times" % times)
        self.prepare_resource(take_video=True, num=times)
        self.gallery.enter()
        self.gallery.open_file(video=True)

        sx, sy, ex, ey = self.gallery.gen_loc_for_swipe(orientation='h', rate_from=0.9, rate_to=0.1)
        ts = int(times / 2)

        self.perform_steps(ts, self.gallery.swipe_file, sx, sy, ex, ey, 10,
                           True)  # def swipe_file(self, sx, sy, ex, ey, steps=10, video=False)
        self.perform_steps(ts, self.gallery.del_file)

        self.mod.back_to_home()
        self.mod.logger.debug("view video in gallery test %d times completed" % times)

    def perform_steps(self, loops, step, *attrs):
        self.mod.logger.info(attrs)
        for loop in range(loops):
            try:
                if attrs is None:
                    if step():
                        self.trace_success()
                    else:
                        self.trace_fail()
                else:
                    if step(*attrs):
                        self.trace_success()
                    else:
                        self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                pass

    def prepare_resource(self, take_video, num):
        '''
        prepare resource for gallery test
        :param take_vidoe:
        :param num:
        :return:
        '''
        try:
            action = self.mod.prepare_video if take_video else self.mod.prepare_pic
            check_action = self.mod.get_screenrecord_number if take_video else self.mod.get_screenshot_number

            self.mod.logger.debug("del all media first")
            self.gallery.enter()
            self.gallery.del_mediafiles_in_gallery()  # del all media file before start test
            self.mod.device.press.home()
            self.mod.start_app('Clock')
            self.mod.logger.debug("prepare resource-{}".format(num))
            action(num)
            actual_num = check_action()
            assert num == actual_num, 'expect take %s resource, but get %s' % (num, actual_num)
            self.mod.logger.debug("prepare resource done")
        except:
            self.mod.save_fail_img()
            # raise
        finally:
            self.mod.device.press.home()

if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestGallery)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
