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
from common.google_music import google_Music
from common.yt_music import YTMusic
from common.native_music import native_Music
from common.mods import Mods
from common.base_test_case import BaseTestCase


class TestMusicPlayer(BaseTestCase):
    test_mod = Mods.Music

    @classmethod
    def setUpClass(cls):
        """必须连接翻墙wifi"""
        super(TestMusicPlayer, cls).setUpClass()
        if cls.c.isMILAN_GL:
            cls.mod = native_Music(cls.c.device, cls.test_mod)
        elif cls.c.isMILAN_EEA:
            cls.mod = native_Music(cls.c.device, cls.test_mod)
        else:
            cls.mod = YTMusic(cls.c.device, cls.test_mod)
        cls.mod.back_to_home()

    def testStability(self):
        self.case_play_music(int(self.dicttesttimes.get("Play_Music".lower())))

    def case_play_music(self, times=1):
        '''play music
        '''
        self.mod.logger.debug("play music test %d times" % times)
        # self.mod.enter()
        for loop in range(times):
            try:
                if self.mod.play_music():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.back_to_home()
        self.mod.close_music()
        self.mod.back_to_home()
        self.mod.logger.debug("play music test %d times complete" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestMusicPlayer)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
