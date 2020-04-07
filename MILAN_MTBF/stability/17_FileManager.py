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
from common.filemanager_tcl import FileManagerTCL
from common.base_test_case import BaseTestCase
from common.mods import Mods

class TestFileManager(BaseTestCase):
    test_mod = Mods.File

    @classmethod
    def setUpClass(cls):
        super(TestFileManager, cls).setUpClass()
        cls.mod = FileManagerTCL(cls.c.device, cls.test_mod)
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")
        cls.mod.clear_background()

    def testStability(self):
        self.file_test(int(self.dicttesttimes.get("File_test".lower())))

    def file_test(self, times=1):
        """case function, m-device call s-device from Dialer、Contact、History
           check call and end call results
        """
        self.mod.logger.info("create, copy, paste, cut, delete folder %d times" % times)
        # folder_name = self.mod.appconfig("cut_paste_folder", "FileManager")
        self.mod.enter()
        self.mod.enter_internal_storage_list()
        for loop in range(times):
            try:
                if self.mod.copy_past() and self.mod.move_past() and self.mod.del_folders():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exception_end_call()

            finally:
                self.mod.device.delay()
                self.mod.back_to_filemanager()

        self.mod.back_to_home()
        self.mod.logger.info("create, copy, paste, cut, delete folder %d times completed" % times)

if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestFileManager)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
