# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import time
import traceback
import unittest

from common.filemanager_tcl import FileManagerTCL
from common.launcher import Launcher

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.base_test_case import BaseTestCase
from common.mods import Mods

class LauncherEndurance(BaseTestCase):
    """
    前置条件
        0. 主屏的Google search widget不能移除，需要用来判定是不是在主屏
        1. 复制大照片到sdcard/wallpaper
        2. 复制40个应用到sdcard/APK
        3. 关闭Google app 检查
        4. filemanager中尝试安装一个应用，跳过向导，允许从filemanager安装应用
    """
    test_mod = Mods.Launcher
    @classmethod
    def setUpClass(cls):
        super(LauncherEndurance, cls).setUpClass()
        cls.mLauncher = Launcher(cls.c.device, cls.test_mod)
        cls.mFileManager = FileManagerTCL(cls.mLauncher.device, 'Filemanager')

        # cls.carrier_service_num = cls.mod.get_carrier_service_num()

    @classmethod
    def tearDownClass(cls):
        super(LauncherEndurance, cls).tearDownClass()

    def setUp(self):
        super(LauncherEndurance, self).setUp()
        self.test_times = int(self.dicttesttimes.get("testtimes".lower()))
        self.mLauncher.clearAllShortcut()

    def testSetWallpaper(self):
        self.logger.info("## start test set wallpaper with big picture")
        startTime = time.time()
        self.logger.info("Set wallpaper")
        loop = 0
        while time.time() - startTime < self.test_times:
            if self.mLauncher.setWallpaper(loop+1):
                self.trace_success()
                self.logger.info('Trace Success Loop')
            else:
                self.logger.warning('Set wallpaper with big picture fail')
                self.mLauncher.save_fail_img()
            loop += 1
        self.logger.info("## end test set wallpaper with big picture")

    def testCreateFolder(self):
        self.logger.info("## start test create folder on home screen")
        startTime = time.time()
        self.logger.info('Create Folder')
        while time.time() - startTime < self.test_times:
            try:
                if self.mLauncher.createFolder() and self.mLauncher.deleteFolder():
                    self.trace_success()
                    self.logger.info('Trace Success Loop')
                else:
                    self.logger.warning("create folder on home screen fail!")
                    self.mLauncher.save_fail_img()
            except Exception:
                self.logger.warning('Create Folder Exception')
                self.logger.error(traceback.format_exc())
                self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
        self.logger.info("## end test create folder on home screen")

    def testOpenCloseFolder(self):
        self.logger.info("## start test open and close folder on home screen")
        startTime = time.time()
        self.logger.info('Open and Close Folder')
        self.mLauncher.createFolder()
        while time.time() - startTime < self.test_times:
            try:
                if self.mLauncher.openFolder() and self.mLauncher.closeFolder():
                    self.trace_success()
                    self.logger.info('Trace Success Loop ')
                else:
                    self.logger.warning('Open and Close Folder Fail')
                    self.mLauncher.save_fail_img()
            except Exception:
                self.logger.warning('Open and Close Folder Exception')
                self.logger.error(traceback.format_exc())
                self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
        self.mLauncher.deleteFolder()
        self.logger.info("## end test open and close folder on home screen")

    def testCreateShortcut(self):
        self.logger.info('## start test create shortcut on home screen')
        startTime = time.time()
        self.logger.info('Create Shortcut')
        while time.time() - startTime < self.test_times:
            try:
                if self.mLauncher.addShortcut(5):
                    self.trace_success()
                    self.logger.info('Trace Success Loop')
                else:
                    self.logger.warning('Create Shortcut Fail')
                    self.mLauncher.save_fail_img()
                self.mLauncher.clearAllShortcut()
            except Exception:
                self.logger.error(traceback.format_exc())
                self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
        self.logger.info('## end test create shortcut on home screen')

    def testChangeIdle(self):
        self.logger.info('## start test change idle screen')
        startTime = time.time()
        self.mLauncher.prepareIdle()
        self.logger.info('Change Idle')
        while time.time() - startTime < self.test_times:
            try:
                if self.mLauncher.changeIdle():
                    self.trace_success()
                    self.logger.info('Trace Success Loop')
            except Exception:
                self.logger.error(traceback.format_exc())
                self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
        self.logger.info('## end test change idle screen')

    def testAddDelDynamicAPP(self):
        self.logger.info('## start test add dynamic app to home screen')
        apps=['Calendar']
        startTime = time.time()
        self.logger.info('Add Dynamic APP')
        while time.time() - startTime < self.test_times:
            try:
                if self.mLauncher.addDynamicApp(apps[0]):
                    self.mLauncher.removeApp(apps[0])
                    self.trace_success()
                    self.logger.info('Trace Success Loop')
                else:
                    self.logger.warning('Add Dynamic App Fail')
                    self.mLauncher.save_fail_img()
            except Exception:
                self.logger.error(traceback.format_exc())
                self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
        self.logger.info('## end test add dynamic app to home screen')

    def testAddWidget(self):
        self.logger.info('## start test add widget on home screen')
        startTime = time.time()
        self.logger.info('Add Widget')
        while time.time() - startTime < self.test_times:
            try:
                if self.mLauncher.addWidget(5):
                    self.trace_success()
                    self.logger.info('Trace Success Loop')
                else:
                    self.logger.warning('Add Widget Fail')
                    self.mLauncher.save_fail_img()
                self.mLauncher.clearAllShortcut()
            except Exception:
                self.logger.error(traceback.format_exc())
                self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
        self.logger.info('## end test add widget on home screen')

    def testInstallAPK(self):
        self.logger.info('## start test Install APK')
        startTime = time.time()
        self.logger.info('Install APK, %s times')
        self.mFileManager.enter()
        self.mFileManager.enter_folder("Installers")
        while time.time() - startTime < self.test_times:
            try:
                if self.mLauncher.installAPK():
                    self.trace_success()
                    self.logger.info('Trace Success Loop')
                else:
                    self.logger.warning('Install APK Fail')
                    self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
                self.mLauncher.uninstallAPK()
            except Exception:
                self.logger.error(traceback.format_exc())
                self.mLauncher.save_fail_img()
                self.mLauncher.backToHome()
        self.logger.info('## end test Install APK')


















    #
    # def test_camera(self):
    #     """
    #     ENDURANCE_CAMERA_PHOTO_001      内存剩余不足情况下拍照         100->20
    #     ENDURANCE_CAMERA_VIDEO_001      内存剩余不足情况下拍摄video    100->20
    #     ENDURANCE_CAMERA_3RDPARTY_001   相机相关APP中相机的应用       100-->remove this case
    #
    #     :return:
    #     """
    #     self.case_take_photo(int(self.dicttesttimes.get("photo_times".lower())))
    #     self.case_take_video(int(self.dicttesttimes.get("video_times".lower())))
    #
    # def case_take_photo(self, times=1):
    #     self.mod.self.logger.info("low storage take photo %d times" % times)
    #     # self.mod.self.logger.info("battery capacity: %s" % self.mod.adb.battery_level())
    #     self.mod.sleep_if_power_low()
    #     for loop in range(times):
    #         try:
    #             self.mod.self.logger.info("start low storage take photo %d" % loop)
    #             if self.mod.take_photo_to_low():
    #                 self.trace_success()
    #         except:
    #             self.mod.self.logger.error(traceback.format_exc())
    #             self.mod.save_fail_img()
    #             self.mod.back_to_home()
    #     self.mod.back_to_home()
    #     self.mod.self.logger.info("low storage take photo %d times completed" % times)
    #     self.mod.self.logger.info("battery capacity: %s" % self.mod.adb.battery_level())
    #
    # def case_take_video(self, times=1):
    #     self.mod.self.logger.info("low storage take video %d times" % times)
    #     self.mod.sleep_if_power_low()
    #     for loop in range(times):
    #         try:
    #             self.mod.self.logger.info("start low storage take video %d" % loop)
    #             if self.mod.take_video_to_low():
    #                 self.trace_success()
    #         except:
    #             self.mod.self.logger.error(traceback.format_exc())
    #             self.mod.save_fail_img()
    #             self.mod.back_to_home()
    #     self.mod.back_to_home()
    #     self.mod.self.logger.info("low storage take video %d times completed" % times)




if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(LauncherEndurance)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
