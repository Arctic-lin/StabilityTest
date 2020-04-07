#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: 01_googleReq.py
@time: 2017/10/11 19:14

information about this file
"""

from __future__ import division

import os
import sys
import traceback
import unittest

# import subprocess
# import random
# import time

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)

from common.settings import Wifi, GoogleReq
from common.telephony import Telephony
from common import utils
import shutil

class TestGoogleReq(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.serinoM = os.environ.get("MDEVICE")
        if cls.serinoM is None:
            cls.serinoM = utils.get_m_device()
        cls.mod = GoogleReq(cls.serinoM, "GoogleReq")
        cls.wifi = Wifi(cls.mod.device, "Wifi")
        cls.tel = Telephony(cls.mod.device, "Tel")

        cls.SDK = cls.mod.adb.get_sdk()
        cls.ANDROID_O = 26
        # get some infor from config file
        # cls.wifi_name = cls.mod.config.getstr("wifi_name", "Wifi", "common")
        # cls.wifi_pwd = cls.mod.config.getstr("wifi_password", "Wifi", "common")
        # cls.wifi_security = cls.mod.config.getstr("wifi_security", "Wifi", "common")

        # connect Wifi
        # cls.wifi.connect_wifi(cls.wifi_name, cls.wifi_pwd, cls.wifi_security)
        source_templates = os.path.dirname(os.path.dirname(__file__)) + "\\TclTools\\templates\\mpchecklist_new.html"
        target_templates = os.path.dirname(os.path.dirname(__file__)) + "\\results\\mpchecklist_new.html"
        shutil.copyfile(source_templates, target_templates)

    @classmethod
    def tearDownClass(cls):
        cls.mod.clear_notification()
        cls.mod.logger.info("Google requirements test Mission Complete")

    def setUp(self):
        self.mod.back_to_home()
        # self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def tearDown(self):
        self.mod.back_to_home()
        # self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def test_001_no_hw_issue(self):
        """
        ID: Case_001
        Summary: No HW issue
        :return:
        """
        # pic_path = self.mod.save_fail_img_adv()
        # screenshot = '<img src="%s" alt="get screeshot failed" width="216" height="324">' % pic_path
        # result = {'{Case_001_ret}': 'NA', '{Case_001_ss}': 'NA'}
        # self.mod.set_mp_result_to_template(result)
        # self.set_result(case_id='Case_001')
        self.mod.logger.debug("Case_001 No HW issue -> NA")

    def test_002_bootlogo(self):
        """
        ID: Case_002
        Summary: Bootlogo
        :return:
        """
        # self.set_result(case_id='Case_002')
        self.mod.logger.debug("Case_002 Bootlogo -> NA")

    def test_003_google_now(self):
        """
        ID: Case_003
        Summary: Google Now
        :return:
        """
        self.mod.logger.debug("Case_003 Google Now")
        ret, screenshot = self.case_google_now()
        self.set_result(case_id='Case_003', ret=ret, ss=screenshot)

    def test_004_geo_match(self):
        """
        ID: Case_004
        Summary: Geo match
        :return:
        """
        self.mod.logger.debug("Case_004 Geo match")
        ret = 'Check via workhelp'
        self.set_result(case_id='Case_004', ret=ret)

    def test_005_setup_wizard(self):
        """
        ID: Case_005
        Summary: Setup Wizard
        :return:
        """
        self.mod.logger.debug("Case_005 Setup Wizard -> NA")

    # @unittest.skip("skip")
    def test_006_Default_Home_Screen_Layout(self):
        """
        ID: Case_006
        Summary: Play store, Google Search
        :return:
        """
        self.mod.logger.debug("test_006_verify_store_search_location")
        ret, screenshot = self.case_verify_store_search_location()
        ret = self._revert_ret_for_cn_variant(ret)
        self.mod.logger.info("ret=%s" % ret)
        self.set_result(case_id='Case_006', pof=ret, ss=screenshot)

    def test_007_verify_google_folder(self):
        self.mod.logger.debug("test_007_verify_google_folder")
        ret, screenshot = self.case_verify_google_folder()
        ret = self._revert_ret_for_cn_variant(ret)
        self.mod.logger.info("ret=%s" % ret)
        self.set_result(case_id='Case_007', ret=ret, ss=screenshot)

    def test_008_unknown_sources(self):
        """
        ID: Case_008
        Summary: unknown sources
        :return:
        """
        self.mod.logger.debug("Case_008 unknown sources")
        self.set_result(case_id='Case_008')

    # def test_009_developer_option(self):
    #     self.mod.logger.debug("test_009_developer_option")
    #     result_value = self.case_develop_option()
    #     if result_value[0] is True:
    #         result_value = self.case_open_develop_option()
    #     self.mod.set_mp_result(result_value[0], "Google Case_009 Developer options", result_value[1])

    def xxxtest_009_developer_option(self):
        """
        ID: Case_009
        Summary: Developer options
        :return:
        """
        self.mod.logger.debug("Case_009 Developer options")
        ret = 'Manual Test'
        self.set_result(case_id='Case_009', ret=ret)

    def test_010_usb_debugging(self):
        """
        ID: Case_010
        Summary: USB debugging
        :return:
        """
        self.mod.logger.debug("Case_010 USB debugging")
        ret = 'Manual Test'
        self.set_result(case_id='Case_010', ret=ret)

    # def test_011_verify_verify_apps(self):
    #     self.mod.logger.debug("test_011_verify_verify_apps")
    #     self.mod.set_mp_result(self.case_verify_apps(), "Google Case_011 Verify apps")

    def test_011_verify_apps(self):
        """
        ID: Case_011
        Summary: Verify apps
        :return:
        """
        self.mod.logger.debug("Case_011 Verify apps")
        ret = 'Manual Test'
        self.set_result(case_id='Case_011', ret=ret)

    def test_012_backup(self):
        """
        ID: Case_012
        Summary: backup
        :return:
        """
        self.mod.logger.debug("Case_012 backup")
        self.set_result(case_id='Case_012')

    def test_013_google_location(self):
        """
        ID: Case_013
        Summary: Google location
        :return:
        """
        self.mod.logger.debug("Case_013 Google location")
        self.set_result(case_id='Case_013')

    def test_014_google_legal(self):
        """
        ID: Case_014
        Summary: Google legal
        :return:
        """
        self.mod.logger.debug("Case_014 Google legal")
        self.set_result(case_id='Case_014')

    def test_015_google_account(self):
        """
        ID: Case_015
        Summary: Google account
        :return:
        """
        self.mod.logger.debug("Case_015 Google account")
        self.set_result(case_id='Case_015')

    def test_016_maps(self):
        """
        ID: Case_016
        Summary: Maps
        :return:
        """
        self.mod.logger.debug("Case_016 Maps")
        self.set_result(case_id='Case_016')

    def test_017_unknown_sources(self):
        """
        ID: Case_017
        Summary: Play Store
        :return:
        """
        self.mod.logger.debug("Case_017 Play Store")
        self.set_result(case_id='Case_017')

    def test_018_(self):
        """
        ID: Case_018
        Summary: YouTube
        :return:
        """
        self.mod.logger.debug("Case_018 Youtube")
        self.set_result(case_id='Case_018')

    def test_019_client_id(self):
        """
        ID: Case_019
        Summary: client id
        :return:
        """
        self.mod.logger.debug("test_019_client_id")
        ret, screenshot = self.case_client_id()
        self.set_result(case_id='Case_019', ret=ret, ss=screenshot)

    def test_020_adb_vendor_id(self):
        """
        ID: Case_020
        Summary: adb的vendor id
        :return:
        """
        self.mod.logger.debug("Case_020 adb vendor id")
        self.set_result(case_id='Case_020')

    def test_021_verify_su_process(self):
        """
        ID: Case_021
        Summary: su proccess
        :return:
        """
        self.mod.logger.debug("test_021_verify_su_process")
        ret, screenshot = self.case_su_process()
        self.set_result(case_id='Case_021', ret=ret, ss=screenshot)

    def test_022_Feature(self):
        """
        ID: Case_022
        Summary: Feature
        :return:
        """
        self.mod.logger.debug("Case_022 Feature")
        self.set_result(case_id='Case_022')

    def test_023_multi_user(self):
        """
        ID: Case_023
        Summary: Multi-user
        :return:
        """
        self.mod.logger.debug("Case_023 Multi-user")
        self.set_result(case_id='Case_023')

    def test_024_waiver_case(self):
        """
        ID: Case_024
        Summary: waiver case
        :return:
        """
        self.mod.logger.debug("Case_024 waiver case")
        self.set_result(case_id='Case_024')

    def test_025_test_report_review(self):
        """
        ID: Case_025
        Summary: test report review
        :return:
        """
        self.mod.logger.debug("Case_025 test report review")
        self.set_result(case_id='Case_025')

    def test_026_check_webview(self):
        """
        ID: Case_026
        Summary: check webview
        :return:
        """
        self.mod.logger.debug("Case_026 check webview")
        self.set_result(case_id='Case_026')

    def test_027_google_settings(self):
        """
        ID: Case_027
        Summary: Google Settings
        :return:
        """
        self.mod.logger.debug("Case_027 Google Settings")
        self.set_result(case_id='Case_027')

    def test_028_factory_reset_protection(self):
        """
        ID: Case_028
        Summary: test_028_factory_rreset_protection
        :return:
        """
        self.mod.logger.debug("Case_028 test_028_factory_rreset_protection")
        self.set_result(case_id='Case_028')

    def test_029_near_ultrasound_capability(self):
        """
        ID: Case_029
        Summary: Near-Ultrasound capability
        :return:
        """
        self.mod.logger.debug("Case_029 Near-Ultrasound capability")
        self.set_result(case_id='Case_029')

    def test_030_verify_apps_for_testing(self):
        self.mod.logger.debug("test_030_verify_apps_for_testing")
        ret, screenshot = self.case_apps_for_testing()
        self.set_result(case_id='Case_030', ret=ret, ss=screenshot)

    def test_031_security_status(self):
        self.mod.logger.debug("test_031_Security status injection into Settings")
        self.set_result(case_id='Case_031')

    # def test_032_verify_backup_transport_Configuration(self):
    #     self.mod.set_result(self.case_backup_ransport_Configuration(), "Google Case_032 Backup Transport Configuration",
    #                         failure_msg="GL devices MUST use GMS transport service")

    def test_032_reference_AOSP_image(self):
        self.mod.logger.debug("test_032_Reference AOSP image")
        self.set_result(case_id='Case_032')

    def test_033_Widget_appearance(self):
        self.mod.logger.debug("test_033_Widget appearance")
        ret = 'Manual Test'
        self.set_result(case_id='Case_033', ret=ret)

    # def test_034_verify_ru_feature(self):
    #     # only need to test in RU device
    #     self.mod.logger.debug("test_034_verify_ru_feature")
    #     self.mod.set_mp_result(self.case_ru_feature(), "Google Case_034 Check that Russia feature string is present")

    def test_034_Russia_feature_string(self):
        self.mod.logger.debug("test_034_Check that Russia feature string is present")
        ret = 'Manual Test'
        self.set_result(case_id='Case_034', ret=ret)

    def test_035_verify_ro_vendor_build_fingerprint(self):
        self.mod.logger.debug("test_035_verify_ro_vendor_build_fingerprint")
        if self.ANDROID_O >= self.SDK:
            ret, screenshot = self.case_ro_vendor_build_fingerprint()
            self.set_result(case_id='Case_035', ret=ret, ss=screenshot)
        else:
            self.mod.logger.info("ignore case 035 ro.vendor.build.fingerprint")
            self.set_result(case_id='Case_035')

    def test_036_verify_safe_mode(self):
        self.mod.logger.debug("test_036_verify_safe_mode")
        ret, screenshot = self.case_safe_mode()
        self.set_result(case_id='Case_036', ret=ret, ss=screenshot)

    def test_037_security_patch_level(self):
        self.mod.logger.debug("test_037_security_patch_level")
        ret, screenshot = self.case_security_patch_level()
        self.set_result(case_id='Case_037', ret=ret, ss=screenshot)

    def test_038_Gboard_device(self):
        self.mod.logger.debug("test_038_Gboard device")
        ret = 'Manual Test'
        self.set_result(case_id='Case_038', ret=ret)

    def test_039_Russia_feature_string(self):
        self.mod.logger.debug("test_039_property ro.product.first_api_level")
        ret = 'Manual Test'
        self.set_result(case_id='Case_039', ret=ret)

    # def test_zz_geo_match(self):
    #     self.mod.set_mp_result("", "Google Case_004 Geo match", testtype="manual")
    #
    # def test_zz_USB_debugging(self):
    #     self.mod.set_mp_result("", "Google Case_010 USB debugging", testtype="manual")

    def _revert_ret_for_cn_variant(self, ret):
        if self.mod.adb.is_cn_variant():
            ret = 'FAIL' if ret == 'PASS' else 'PASS'
        return ret

    def set_result(self, case_id, pof='',ret="", ss=''):
        """
        pof:pass/fail
        result:结果
        :rtype: object
        """
        ret_key = '{%s_ret}' % case_id
        ss_key = '{%s_ss}' % case_id
        pof_key = '{%s_pof}' % case_id

        if pof =="FAIL":
            pof = "<p style='background-color:#FF0000'>%s</p>" % pof
        elif  pof =="PASS":
            pof = "<p style='background-color:#C6EFCE'>%s</p>" % pof
        elif pof =="Manual Test":
            pof = "<p style='background-color:#F7FE2E'>%s</p>" % pof
        result = { pof_key:pof, ret_key: ret, ss_key: ss,}
        self.mod.set_mp_result_to_template(result)


    def case_open_develop_option(self):
        try:
            self.mod.enter_settings("About phone")
            self.mod.device.wait("idle")
            self.mod.device(scrollable=True, resourceId="com.android.settings:id/list").scroll.vert.to(
                text="Build number")
            build_info = self.mod.device(text="Build number").info
            top, bottom, left, right = build_info["bounds"]["top"], build_info["bounds"]["bottom"], \
                                       build_info["bounds"]["left"], build_info["bounds"]["right"]
            center_coordinate = ((top + bottom) / 2, (left + right) / 2)
            for i in range(10):
                self.mod.device.click(center_coordinate[1], center_coordinate[0])
            self.mod.device.press.back()
            self.mod.device.wait("idle")
            if self.mod.device(scrollable=True, resourceId="com.android.settings:id/dashboard_container").scroll.vert. \
                    to(text="Developer options"):
                self.mod.logger.info("The title Developer options exists")
                return True, ""
            else:
                return False, "can't open developer options by click build number"
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return False, "got exception, check your script"

    def case_develop_option(self):
        try:
            self.mod.start_app("Settings")
            self.mod.device.wait("idle")
            if self.mod.device(scrollable=True,
                               resourceId="com.android.settings:id/dashboard_container").scroll.vert.to(
                    text="Developer options"):
                self.mod.logger.info("The title Developer options exists")
                return False, "Developer options exists"
            self.mod.logger.info("The title Developer options does not exists")
            self.mod.back_to_home()
            return True, "Developer options does not exists"
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return False, "got exception, check your script"

    def case_client_id(self):
        try:
            # self.tel.dialer_secret_code("*#*#759#*#*")
            # self.mod.device.delay(2)
            # self.mod.device(text="View Client IDs").click.wait()
            # assert self.mod.device(text="Client IDs").wait.exists(), "Can't find the client IDs"
            # client_id_value = self.mod.device(resourceId="android:id/message").get_text()
            # self.mod.logger.info("Client IDs get")
            # return "to check", client_id_value
            ret, _ = self.mod.adb.shell2('getprop | grep clientid')
            ret_str = '<br />'.join(ret.split())
            screen = 'NA'
            return ret_str, screen
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_security_patch_level(self):
        try:
            patch_level_shell, _ = self.mod.adb.shell2("getprop ro.build.version.security_patch")
            self.mod.enter_settings("System")
            if self.mod.device(scrollable=True):
                self.mod.device(scrollable=True).scroll.vert.to(text="About phone")
            self.mod.device(text="About phone").click.wait()

            menu_item = self.mod.device(text="Android security patch level")
            patch_level_settings = menu_item.sibling(resourceId="android:id/summary").get_text()

            self.mod.device.delay(1)
            screen = self.mod.save_fail_img_adv()

            self.mod.logger.info("security_patch_level: %s; %s" % (patch_level_shell, patch_level_settings))
            return patch_level_shell.strip() + "(shell); <br />" + patch_level_settings + "(settings)", screen
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_verify_store_search_location(self):
        """
        # check the play store and Google search, they should be in home screen
        :return:
        """
        try:
            # back to home
            self.mod.device.press.home()
            self.mod.device.press.home()

            self.mod.device.delay()
            screen = self.mod.save_fail_img_adv()
            # check play store in home screen or not
            is_store_exists = self.mod.verify_play_store()

            # check Google search in home screen or not
            is_search_exists = self.mod.verify_Google_search()

            is_default_search, screen1 = self.mod.verify_default_search()

            # todo Google search是系统默认search，

            ret = 'PASS' if is_store_exists and is_search_exists and is_default_search else "FAIL"
            return ret, screen + screen1
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_verify_google_folder(self):
        """
        check Google folder, the folder MUST be named Google,
        and the order of core app must be:Google, Chrome, Gmail, Maps, YouTube, Drive, Play Music, Duo, Photos
        :return:
        """
        try:
            # back to home screen
            self.mod.device.press.home()
            self.mod.device.press.home()

            # verify Google folder and its order
            return self.mod.verify_google_folder()
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_su_process(self):
        """
        adb shell su, should return 'su: not found'
        :return:
        """
        try:
            if self.mod.check_su_process():
                return 'PASS', ''
            else:
                return 'FAIL', ''
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_backup_ransport_Configuration(self):
        """
        adb shell bmgr list transports, '*' identify which mode using
            android/com.android.internal.backup.LocalTransport
          * com.google.android.gms/.backup.BackupTransportService
        :return:
        """
        try:
            return self.mod.check_backup_transport()
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return False

    def case_ru_feature(self):
        """
        Run adb shell pm list features
        Verify the following line is present com.google.android.feature.RU
        the feature will shows only when ECID = RU????
        :return:
        """
        try:
            return self.mod.check_ru_feature_string()
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return False

    def case_ro_vendor_build_fingerprint(self):
        """
        this case only test on Android O, SDK >=26
        :return:
        """
        try:
            if self.mod.check_vendor_build_fingerprint():
                return 'PASS', ''
            else:
                return 'FAIL', ''

        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_safe_mode(self):
        """
        long press power,
        then lang press power off,
        check the safe mode layout
        :return:
        """
        try:
            return self.mod.check_safe_mode()

        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_verify_apps(self):
        """
        login google account,
        verify setting->Google-security>-verify apps>Scan device for security threats if on
        :return:
        """
        try:

            return self.mod.verify_verify_apps()

        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return False

    def case_apps_for_testing(self):
        """
        iterate all apps, get apps name, check weather 'test' in the app name
        :return:
        """
        white_list = {"com.github.uiautomator.test"}

        try:
            app_list = self.mod.check_test_app_in_apps()
            test_apps = []
            for app in app_list:
                if "test" in app.lower():
                    if app not in white_list:
                        self.mod.logger.info("find test app in Settings-Apps: %s" % str(app))
                        test_apps.append(app)

            if len(test_apps) > 0:
                temp_str = '<br />'.join(test_apps)
                return temp_str, ''
            else:
                return 'PASS', ''

        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_google_now(self):
        """
        1.检查Google Now是否预制
        2.同时验证assist action
        :return:
        """
        try:
            # back to home screen
            self.mod.device.press.home()
            self.mod.device.press.home()

            self.mod.adb.longPressHome()
            self.mod.device.delay(2)
            screen = self.mod.save_fail_img_adv()
            self.mod.device.delay(2)
            return 'Check screenshot', screen

        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            return 'FAIL', "got exception, check your script"


if __name__ == "__main__":
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestGoogleReq)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
