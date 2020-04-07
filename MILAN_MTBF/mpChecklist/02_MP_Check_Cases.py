#!/usr/bin/python2
# -*- coding: utf-8 -*-
import csv
import os
import subprocess
import sys
import time
import traceback
import unittest

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)
from common.settings import Settings
from common.telephony import Telephony
from common import utils
import os
import shutil


class SettingRelated(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.serinoM = os.environ.get("MDEVICE")
        if cls.serinoM is None:
            cls.serinoM = utils.get_m_device()

        cls.set = Settings(cls.serinoM, "settings")
        cls.tel = Telephony(cls.set.device, "Telephony")
        source_templates = os.path.dirname(os.path.dirname(__file__)) + "\\TclTools\\templates\\mpchecklist_new.html"
        target_templates = os.path.dirname(os.path.dirname(__file__)) + "\\results\\mpchecklist_new.html"
        shutil.copyfile(source_templates, target_templates)

    def setUp(self):
        self.set.back_to_home()

    def tearDown(self):
        self.set.back_to_home()

    def test_Fingerprint_001(self):
        """Fingerprint_adb shell getprop ro.build.fingerprint
        """
        sw = self.set.adb.get_prop("ro.oem.build_id")
        expected_result = self.set.config_mp.get(self.set.project_name, "fingerprint").replace("$$$$", sw)
        self.set.logger.debug("test_Fingerprint_001 Fingerprint_adb shell getprop ro.build.fingerprint")
        ret = self.set.adb.get_prop("ro.build.fingerprint")#实际结果
        pass_or_fail = "PASS" if ret == expected_result else "FAIL"
        self.set_result(case_id='Fingerprint_001', pof=pass_or_fail, ret=ret)

    def test_model_001(self):
        """Model_*#837837#
        """
        self.set.logger.debug("test_model_001 Model_*#837837#")
        ret, screenshot = self.case_model_001()
        expected_result = self.set.config_mp.get(self.set.project_name, "product_name")
        pass_or_fail = "PASS" if ret == expected_result else "FAIL"
        self.set_result(case_id='Model_001', pof = pass_or_fail,ret=ret, ss=screenshot)

    def test_baseOS_001(self):
        """
        BaseOS_adb shell getprop ro.build.version.base_os
        :return:
        """
        self.set.logger.debug("test_baseOS_001 BaseOS_adb shell getprop ro.build.version.base_os")
        ret = self.set.adb.shell('getprop ro.build.version.base_os').strip()
        expected_result = self.set.config_mp.get(self.set.project_name, "base_os")
        pass_or_fail = "PASS" if ret == expected_result else "FAIL"
        self.set_result(case_id='BaseOS_001', ret=ret, pof=pass_or_fail)

    def xxxtest_UA_001(self):
        """
        UA profile(browse, MMS)
        :return:
        """

    def test_SVN_001(self):
        """
        SVN
        :return:
        """
        # self.set.logger.debug("test_SVN_001 SVN")
        # ret, screenshot = self.case_svn_001()
        # print "ret:'%s'"%ret
        print "self.set.project_name:", self.set.project_name
        expected_result = self.set.config_mp.get(self.set.project_name, "imei_sv")
        print "expected_result:'%s'" % expected_result
        # pass_or_fail = "PASS" if ret == expected_result else "FAIL"
        # print "pass_or_fail:",pass_or_fail
        # self.set_result(case_id='SVN_001', ret=ret, ss=screenshot,pof=pass_or_fail)

    def test_API_001(self):
        """
        test API level adb shell getprop ro.product.first_api_level
        :return:
        """
        self.set.logger.info("test_API_001 adb shell getprop ro.product.first_api_level")
        ret, err = self.set.adb.shell2("getprop ro.product.first_api_level")
        if err != "":
            self.set.logger.info("Fail to get first api level: " + err)
            ret = err
        ret = ret.strip()
        self.set.logger.info("First api level is: " + str(ret.strip()))
        expected_result = self.set.config_mp.get(self.set.project_name, "first_api_level")
        pass_or_fail = "PASS" if ret == expected_result else "FAIL"
        self.set_result(case_id='API_001', ret=ret, pof=pass_or_fail)

    def test_Hidden_Code_001(self):
        """
         check hidden code *#*#0574#*#*, it should not have any changes (enter feedback apk or open logcat)
        *#*#0574#*#*_log Closed
        :return:
        """
        self.set.logger.debug("test_Hidden_Code_001 *#*#0574#*#*_log Closed")
        screen = self.check_should_none("*#*#0574#*#*")
        self.set_result(case_id='Hidden Code_001', ss=screen)

    def test_Hidden_Code_002(self):
        """
        Hidden Code_002
        check hidden code *#*#2887#*#*, it should not have any changes (pop up robust window)
        *#*#2887#*#*_no Changes
        :return:
        """
        self.set.logger.debug("test_Hidden_Code_002 ")
        pof, screen = self.check_should_none1("*#*#2887#*#*")
        self.set_result(case_id='Hidden Code_002', ss=screen, pof=pof)

    def test_Hidden_Code_003(self):
        """
        Hidden Code_003
        ##782#_Version Information
        get parameter version by hidden code ##782#
        :return:
        """
        self.set.logger.debug("test_Hidden_Code_003 ##782#_Version Information")
        ret, screen = self.get_parameters_version()
        self.set_result(case_id='Hidden Code_003', ret=ret, ss=screen)

    def test_Hidden_Code_005(self):
        """
        Hidden Code_005
        *#*#212018#*#*_no Changes
        check that hidden code *#*#212018#*#* can't root the device
        :return:
        """
        self.set.logger.debug("test_Hidden_Code_005 *#*#212018#*#*_no Changes")
        ret, screen = self.check_should_none1("*#*#212018#*#*")
        self.set_result(case_id='Hidden Code_005', pof=ret, ss=screen)

    def test_Hidden_Code_006(self):
        """
        Hidden Code_006
        *#2886#_Version Information
        :return:
        """
        self.set.logger.debug("test_Hidden_Code_006 *#2886#_Version Information")
        ret, screen = self.case_hidden_code_006()
        self.set_result(case_id='Hidden Code_006', ret=ret, ss=screen)



    def test_Debug_Property_002(self):
        """
        Debug Property_002
        Check SDM_Install boom.apk
        :return:
        """
        self.set.logger.debug("test_Debug_Property_002 Check SDM_Install boom.apk")
        ret, screen = self.check_boom_apk()
        self.set_result(case_id='Debug Property_002', pof=ret, ss=screen)

    def test_Debug_Property_003(self):
        """
        Debug Property_003
        Check Stagefright_Install Stagefright Detector.apk
        :return:
        """
        self.set.logger.debug("test_Debug_Property_003 Check Stagefright_Install Stagefright Detector.apk")
        ret, screen = self.check_stagefright()
        self.set_result(case_id='Debug Property_003', pof=ret, ss=screen)

    def xxxtest_Debug_Property_004(self):
        """
        removed!
        Debug Property_004
        ADB log_Disable
        :return:
        """
        self.set.logger.debug("test_Debug_Property_004 ADB log_Disable")
        # todo: how to verify the correct status
        ret = 'Manual Test'
        self.set_result(case_id='Debug Property_004', ret=ret)

    def xxtest_APK_Check_001(self):
        """
        APK Check_001
        Check 3rd APK list
        check that the APK list in DUT is correct
        :return:
        """
        self.set.logger.debug("test_APK_Check_001  Check 3rd APK list")
        ret, screen = self.case_app_list3()
        self.set.logger.debug(ret)
        self.set_result(case_id='APK Check_001', ret=ret, ss=screen)

    def test_APK_Check_002(self):
        """
        APK Check_002
        StabilityMonitor APK_Removed
        check that StabilityMonitor APK was removed
             1. check *#*#0574762#*#*
             2. check app list
        :return:
        """
        self.set.logger.debug("test_APK_Check_002  StabilityMonitor APK_Removed")
        ret, screen = self.check_should_none1("*#*#0574762#*#*")
        ret1, screen1 = self.check_app_not_exist("StabilityMonitor")

        f_ret, scr = "PASS", screen + screen1 if ret == ret1 == 'PASS' else "FAIL"

        self.set_result(case_id='APK Check_002', pof=f_ret, ss=screen + screen1)

    def test_APK_Check_003(self):
        """
        APK Check_003
        OneTouchFeedback and SafeGuard APK_Removed
        :return:
        """
        self.set.logger.debug("test_APK_Check_003  OneTouchFeedback and SafeGuard APK_Removed")
        ret, screen = self.check_app_not_exist("Feedback")
        ret1, screen1 = self.check_app_not_exist("Safe Guard")

        f_ret = 'PASS' if ret == ret1 == 'PASS' else '%s; %s' % (ret, ret1)

        self.set_result(case_id='APK Check_003', ret=f_ret, ss=screen + screen1)

    def xxxxtest_APK_Check_004(self):
        """
        APK Check_004
        Insert CN SIM Cards_GMS APK Enabled
        :return:
        """
        self.set.logger.debug("test_APK_Check_004  Insert CN SIM Cards_GMS APK Enabled")
        ret = 'Manual Test'
        self.set_result(case_id='APK Check_004', ret=ret)

    def test_APK_Check_005(self):
        """
        APK Check_005
        ddt.tkn OFF_Battery log APK removed
            1. main menu查看BatteryLog app
            2. Settings->Apps查看BatteryLog app   --   如果测试机曾经有加载过ddt token，Apps里会有BatteryLog，
            和SPM确认正常现象，出货手机不会有
            3. 长按power键查看“Take bug report" option（开机向导前后都要查看）  --
            同上，如果曾经加载过ddt token，开机向导前会有此option，正常现象
            4. 异常重启或长按power键重启查看是否会弹出“Reset Survey”界面 -- NOT SUPPORT,
            和Li Weifeng确认，模拟不了长按重启，此功能是硬件功能
        :return:
        """
        self.set.logger.debug("test_APK_Check_005   ddt.tkn OFF_Battery log APK Removed")
        ret, screen = self.check_batterylog_app()
        self.set_result(case_id='APK Check_005', pof=ret, ss=screen)

    def test_APK_Check_006(self):
        """
        APK Check_006
        Check support center
        :return:
        """
        self.set.logger.debug("test_APK_Check_006  Check support center")
        ret, screen = self.case_app_check_006()
        self.set_result(case_id='APK Check_006', pof=ret, ss=screen)

    def test_APK_Check_007(self):
        """
        APK Check_007
        Remove Robust from MP Branch
        :return:
        """
        # com.tct.robust
        self.set.logger.debug("test_APK_Check_007 Remove Robust from MP Branch")
        robust = 'com.tct.robust'
        ret = 'PASS' if not self.is_in_package_list(robust) else 'FAIL'
        self.set_result(case_id='APK Check_007', pof=ret)

    def xxtest_ASDiv_001(self):
        """
        Enable ASDive_ Hidden
        :return:
        """
        self.set.logger.debug("test_ASDiv_001 Enable ASDive_ Hidden")
        # test_result = self.check_ASDive()
        self.set_result(case_id='ASDiv_001', ret='REMOVED')

    def xxtest_ASDiv_002(self):
        """
        ASDiv_Opened
        :return:
        """
        self.set.logger.debug("test_ASDiv_002 ASDiv_Opened")
        self.set_result(case_id='ASDiv_002', ret='REMOVED')

    def test_SAR_001(self):
        """
        Enable SAR
        :return:
        """
        self.set.logger.debug("test_SAR_001 Enable SAR")
        stdout, stderr = self.set.adb.shell2("getprop persist.sys.sar.enabled")

        if ("1" in stdout) or ("1" in stderr):
            self.set.logger.debug("sar is enabled")
            ret = 'PASS'
        else:
            self.set.logger.debug("sar is disabled")
            ret = 'FAIL'
        self.set_result(case_id='SAR_001', pof=ret,ret=stdout.strip())

    def test_Settings_001(self):
        """
        T1 N/A
        #*debugmode*#open_USB Debug OFF
        :return:
        """
        self.set.logger.debug("test_Settings_001 #*debugmode*#open_USB Debug OFF")
        ret = 'Manual Test'
        self.set_result(case_id='Settings_001', ret=ret)

    def test_Settings_002(self):
        """
        System update_Removed
        :return:
        """
        self.set.logger.debug("test_Settings_002 System update_Removed")
        ret, screen = self.check_remove_system_update()
        self.set_result(case_id='Settings_002', ret=ret, ss=screen)

    def test_Settings_003(self):
        """
        HAC Item_Check
        1. Phone -> Settings -> Accessibility -> Hearing adis
        2. 除北美外，其他区域都不需要HAC
        3. 北美ECID:10534,10517,10515,10518,50,539,544,10539保留该菜单
        FR 4901511 for mercury
        :return:
        """
        self.set.logger.debug("test_Settings_003 HAC Item_Check")
        ret, screen = self.check_HAC()
        self.set_result(case_id='Settings_003', ret=ret, ss=screen)

    def test_Settings_004(self):
        """
        Remove navigation gesture from developer option
        :return:
        """
        self.set.logger.debug("test_Settings_004 Remove navigation gesture from developer option")

        # check devleoper option, set result to case_010
        if self.set.enable_dev_mode():
            self.set_result(case_id='Case_009', ret='PASS')
            ret, screen = self.case_settings_004()
            self.set_result(case_id='Settings_004', ret=ret, ss=screen)
        else:
            self.set_result(case_id='Case_009', ret='FAIL')
            self.set_result(case_id='Settings_004', ret='FAIL')


    def xxxtest_Google_002(self):
        """
        CN GMS_removed
        :return:
        """
        self.set.logger.debug("test_Google_002 CN GMS_removed")

        product_name = self.set.adb.get_product_name()
        blacklist = ['com.google.android.marvin.talkback',
                     'com.google.android.apps.messaging.overlay',
                     'com.google.android.webview',
                     'com.google.android.tag']

        if 'cn' in product_name.lower():
            # if self.set.adb.is_cn_variant():
            google_apps = [p for p in self._yeild_package_with_google() if p not in blacklist]
            if len(google_apps) == 0:
                self.set.logger.info("no Google apps")
                self.set_result(case_id='Google_002', ret='PASS')
            else:
                self.set.logger.info("found Google apps: %s" % google_apps)
                self.set_result(case_id='Google_002', ret=';'.join(google_apps))
        else:
            self.set.logger.info("%s is not CN variant" % product_name)
            self.set_result(case_id='Google_002', ret='PASS', ss='Not CN variant')

    def test_Hidden_Code_004(self):
        """
        Hidden Code_004
        ###666#_no Changes
        check that hidden code ###666# will not disable GMS applications (otherwise it will pop up a window)
        :return:
        """
        self.set.logger.debug("test_Hidden_Code_004 ###666#_no Changes")
        ret, screen = self.check_should_none2("###666#")
        self.set_result(case_id='Hidden Code_004', pof=ret, ss=screen)

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
        self.set.set_mp_result_to_template(result)

    def _yeild_package_with_google(self):
        packages = self.set.adb.shell('pm list packages').split()
        for packcage in packages:
            if 'google' in packcage:
                yield packcage.split(':')[1].strip()

    # # @unittest.skip("skip")
    # def test_zz_Setup_Wizard_001(self):
    #     self.set.set_mp_result("", "Setup_Wizard_001 Remove Skip Setup Wizard connect WiFi step", testtype="manual")
    #
    # # @unittest.skip("skip")
    # def test_zz_UA_001(self):
    #     self.set.set_mp_result("", "UA_001 UA profile(browse, MMS)", testtype="manual")
    #
    # def test_zz_SVN_001_QXDM(self):
    #     self.set.set_mp_result("", "SVN_001 SVN(QXDM)", testtype="manual")
    #
    # def test_zz_APK_Check_005(self):
    #     self.set.set_mp_result("", "APK_Check_005 ddt.tkn OFF_Battery log APK Removed(long press power)", testtype="manual")

    def case_app_list3(self):
        self.set.logger.info("check app via package name")
        try:
            # read csv file, target
            filename, apps_target = self._app_list()
            self.set.logger.info("filename: %s" % filename)
            if len(filename) == 0:
                return 'FAIL', "Can not find app list file"
            elif not apps_target:
                return 'FAIL', "model name do set, check your script"

            # get app packages info form device
            apps_device = self.set.adb.shell('pm list packages -f').split()

            missed_apps = []
            not_matched_apps = []

            # iterate target
            for app_pac, app_attr in apps_target.items():
                app_device = self._gen_matched_data(app_pac, apps_device)
                if app_device is None:  # target app do not match
                    missed_apps.append('%s,%s' % (app_attr[0], app_attr[1]))  # add app name, app type(pre-load or PAI)
                    self.set.logger.info("package %s missed" % app_pac)
                else:  # target app matched, go to attribute check process
                    info = self._match_attr(app_attr, app_device)
                    if info is not None:
                        not_matched_apps.append(info)
                        self.set.logger.info("package %s found" % app_pac)

            self.set.logger.info("missed_apps: %s" % missed_apps)
            self.set.logger.info("not_matched_apps: %s" % not_matched_apps)
            # check Google apps

            # generate string for report
            ret = self._generate_str(missed_apps, not_matched_apps)
            return filename + ret, ''
        except:
            self.set.logger.warning(traceback.format_exc())
            return 'FAIL', "got exception, check your script"

    def _match_attr(self, app_attr, app_device):
        app, type, is_unistall = app_attr
        package = app_device.split('=')[-1]
        # specific data, 如果有需要忽略的关键字，用元组作为值，组成一个字典
        removeable_kw = ('/data/', 'removeable-app')
        not_uninstall_pack = ('com.android.vending', 'com.google.android.gms')
        is_unistall_dev = 'N'

        # normal judge
        for item in removeable_kw:
            if item in app_device:
                is_unistall_dev = 'Y'
                break

        # handle exception
        if package in not_uninstall_pack:
            is_unistall_dev = 'N'

        # verify result
        if is_unistall == is_unistall_dev:
            return None
        return '%s uninstall expect %s, but got %s. ' % (app, is_unistall, is_unistall_dev)

    def _gen_matched_data(self, package, apps_device):
        """

        :param package: package from csv file
        :param apps_device: packages from device
        :return: if target package name not in device, return none, else return the package all info
        """
        for app_device in apps_device:
            if package in app_device:
                return app_device
        return None

    def _generate_str(self, missed_apps, not_matched_apps):
        missed_str = "<br />All App matched requirement"
        not_matched_str = "<br />All App uninstall attribute matched requirement"

        if len(missed_apps):
            missed_str = "<br />Can not find some app:" + "<br />".join(missed_apps)
        if len(not_matched_apps):
            not_matched_str = "<br />Some app uninstall attribute failed:" + "<br />".join(not_matched_apps)

        return missed_str + not_matched_str

    def _app_list(self):
        """
        读取手机的model name，用于匹配variant列
        读取配置文件到一个字典
        :return:{pac: (appname, type, uninstall)}
        """
        csv_loc = r'\\172.16.11.11\val\08_Share\00_PerformanceReport\Athena\05_Customization\MPChecklist\z_APPList_z'
        csv_name = self._get_name(csv_loc)
        if csv_name is None:
            return False, False
        csv_path = csv_loc + os.sep + csv_name
        model_name = self.set.adb.get_product_name()
        self.set.logger.info("ro.vendor.product.name: %s" % model_name)
        adict = {}
        with open(csv_path, 'r') as f_in:
            reader = csv.DictReader(f_in)
            temp = reader.fieldnames
            self.set.logger.info("fieldnames:%s" % temp)
            if model_name not in reader.fieldnames:
                return False, False
            for row in reader:
                pack = row['Package'].strip()
                app = row['App'].strip()
                type = row['Type'].strip()
                uninstall = row['uninstall (Y/N)'].strip()
                variant = row[model_name].strip()
                if '.' in pack and 'Y' in variant:
                    self.set.logger.info("%s:(%s, %s, %s %s)" % (pack, app, type, uninstall, variant))
                    adict[pack] = (app, type, uninstall)
        return csv_name, adict

    def case_app_list2(self):
        self.set.logger.info("get app text from apps & notifications->see all->show system")
        try:
            self.set.enter_settings('Apps & notifications')
            self.set.device(scrollable=True).scroll.vert.to(textContains="See all")
            self.set.device(textContains="See all").click()
            assert self.set.device(text="App info").wait.exists(), "**** enter app info failed  ****"

            self.set.device(description="More options").click()
            self.set.device.wait.idle()
            self.set.device(text="Show system").click()
            self.set.device.wait.idle()

            end_text = self.get_end_text()
            self.set.device(resourceId="android:id/list").fling.vert.toBeginning(max_swipes=100)
            f_app = self.get_text(end_text)
            return '<br />'.join(f_app), ''
            # while end_text not in self.get_text():
            #     self.set.device(resourceId="android:id/list").scroll.vert.forward(steps=100)
        except:
            self.set.logger.warning(traceback.format_exc())
            return 'FAIL', "got exception, check your script"

    def case_app_list(self):
        try:
            stdout, stderr = self.set.adb.shell2("pm list packages -e")
            print stdout
            # write current test's app list to package_list.txt
            current_test_file_path = self.set.log_path + os.sep + "package_list.txt"
            current_test_file = open(current_test_file_path, 'w')
            current_test_file.write(stdout)
            current_test_file.close()

            file_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "test_file"
            app_fie_path = file_path + os.sep + "package_list.txt"
            print app_fie_path
            app_file = open(app_fie_path, 'r')
            app_lines = app_file.read().split("\r")
            absence_app = []
            for app in app_lines:
                app = app.strip()
                if app == "":
                    continue
                if app not in stdout:
                    self.set.logger.error("can't find app: " + app)
                    absence_app.append(app)
            app_file.close()
            if len(absence_app) > 0:
                return 'FAIL', "can't find: %s" % str(absence_app)
            else:
                return "PASS", ""
        except:
            self.set.logger.warning(traceback.format_exc())
            return 'FAIL', "got exception, check your script"

    def get_text(self, end_text):
        f_app = []
        while True:
            apps = self.text_generator()
            f_app += apps
            self.set.device(resourceId="android:id/list").scroll.vert.forward(steps=100)
            if end_text in apps:
                break
            self.set.device(resourceId="android:id/list").scroll.vert.forward(steps=100)
            self.set.device.delay()
        return f_app

    def text_generator(self):
        apps = set()
        title_content = self.set.device(resourceId="android:id/title")
        for _index in range(title_content.count):
            list_content = self.set.device(resourceId="android:id/list")
            _text = list_content.child(index=_index).child(resourceId="android:id/title").get_text()
            apps.add(_text)
            print _text
        return apps

    def get_end_text(self):
        self.set.device(resourceId="android:id/list").fling.vert.toEnd(max_swipes=100)
        title_count = self.set.device(resourceId="android:id/title").count
        list_content = self.set.device(resourceId="android:id/list")
        end_text = list_content.child(index=(title_count - 1)).child(resourceId="android:id/title").get_text()
        self.set.logger.info("end test is %s" % end_text)
        return end_text

    def case_root(self):
        try:
            self.tel.dialer_secret_code("*#*#212018#*#*")
            self.set.device.delay(2)
            return (not self.set.adb.is_kw_in_shell_output(cmd="ls system/xbin", keywords="su")), ""

        except:
            self.set.logger.warning(traceback.format_exc())
            return False, "got exception, check your script"

    def check_HAC(self):
        """Check whether has HAC item in phone settings"""
        try:
            cmd = "am start com.android.phone/.settings.AccessibilitySettingsActivity"
            self.set.adb.shell2(cmd)

            self.set.device.delay()
            screen = self.set.save_fail_img_adv()

            if self.set.device(text="Accessibility").wait.exists():
                if self.set.device(text="Hearing aids").exists:
                    self.set.logger.debug("the hearing aids item exists")
                    self.set.save_fail_img()
                    return 'PASS', screen
                else:
                    self.set.logger.debug("the hearing aids item does not exists")
                    self.set.save_fail_img()
                    return 'FAIL', screen
            self.set.logger.debug("can not enter Accessibility Menu, fail")
            self.set.save_fail_img()
            return "FAIL", "can not enter Accessibility Menu, please check your script"
        except:
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return "FAIL", "got exception, check your script"

    def check_remove_system_update(self):
        try:
            self.set.enter_settings("System")
            self.set.device.wait("idle")

            is_updates_exist = self.set.device(textContains="updates").wait.exists(timeout=3000)
            if is_updates_exist:
                self.set.logger.info("'%s' exists" % "system updates")
                screen = self.set.save_fail_img_adv()
                return 'FAIL', screen

            self.set.back_to_home()
            self.set.start_app("Settings")
            self.set.device.wait("idle")
            self.set.device(resourceId="com.android.settings:id/search_action_bar").click.wait()
            if self.set.device(resourceId="android:id/search_src_text").wait.exists():
                self.set.device(resourceId="android:id/search_src_text").set_text("sys")
                self.set.device.wait("idle")
                if self.set.device(scrollable=True, resourceId="com.android.settings:id/list_results").scroll.vert.to(
                        textContains="updates"):
                    self.set.logger.info("'%s' exists" % "system updates")
                    screen = self.set.save_fail_img_adv()
                    return False, screen
                self.set.logger.info("the item system updates does exists in search result")
                return 'PASS', ""
            else:
                self.set.logger.info("enter settings search fail")
                self.set.save_fail_img()
                return 'FAIL', "can't enter search, please check your script"
        except:
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return False, "got exception, check your script"

    def check_ASDive(self):
        try:
            self.tel.dialer_secret_code("*#*#46368676#*#*")
            self.set.device.delay(2)
            if self.set.device(textContains="ASDiv").exists:
                self.set.logger.debug("ASDiv exists, FAIL")
                self.set.save_fail_img()
                return False, "ASDiv exists in 46368676"
            return True, ""
        except:
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return False, "got exception, check your script"

    def check_batterylog_app(self):
        try:
            # check in power off page
            self.long_press_power(2)
            self.set.device.delay(2)
            screen = self.set.save_fail_img_adv()
            ret = 'PASS'
            if self.set.device(text="Power off").wait.exists():
                icon_count = self.set.device(resourceId="android:id/icon").count
                if (icon_count > 3) or self.set.device(text="Take bug report").exists:
                    self.set.logger.debug("take bug report item exists, FAIL")
                    self.set.save_fail_img()
                    ret = "FAIL, tack bug report exists"

            # check in app list
            ret1, screen1 = self.check_app_not_exist("BatteryLog")

            # if return_value_app[0]:
            #     self.set.save_fail_img()
            #     return False, "BatteryLog APP exists"

            f_ret = 'PASS' if ret == ret1 == 'PASS' else ret + '; ' + ret1
            return f_ret, screen + screen1
        except:
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return 'FAIL', "got exception, check your script"

    def check_boom_apk(self):
        apk_name = "boom.apk"
        if not self.install_apk(apk_name):
            return 'FAIL', 'Fail to install boom'
        self.set.start_app("Boom Test")
        self.set.device(text="CONTINUE").click()
        self.set.device(text="OK").click()
        try:
            self.set.device.delay()
            self.set.device(description="Clear all").click.wait()
            self.set.device.delay()
            if self.set.device(packageName="com.tcl.android.launcher").wait.exists():
                self.set.logger.info("boom test pass")
                return 'PASS', ""
            return "FAIL", "Fail to click clear all button"
        except:
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return 'FAIL', "got exception, check your script"

    def dial_secret_code(self, secret_code):
        print "dial secret code: %s" % secret_code
        cmd = 'am start -a com.android.HiddenMenu.START -n com.android.HiddenMenu/com.android.HiddenMenu.HiddenAppTop --es hidden_key "%s"' % secret_code
        return_value = self.set.device.server.adb.enter_shell_cmd(cmd)
        print "the return of the secret code: ", return_value

    def check_stagefright(self):
        # 1. install Stagefright Detector;    2. run Stagefright Detector;
        try:
            if not self.install_apk("com.zimperium.stagefrightdetector.apk"):
                return "FAIL to install stagefright detector", ''
            self.set.start_app("Stagefright Detector")
            self.set.device(text="BEGIN ANALYSIS").click.wait()
            self.set.device.delay(15)

            if self.set.device(text="Not Vulnerable").wait.exists(timeout=30000):
                status = "PASS"
            else:
                status = "FAIL"

            screen = self.set.save_fail_img_adv()
            return status, screen
        except:
            self.set.logger.info("exception to get check stagefright")
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return 'FAIL', "got exception, check your script"

    def check_should_none(self, code_num):
        self.set.logger.info("try to check whether the %s is closed" % code_num)
        try:
            self.tel.dialer_secret_code(code_num)
            self.set.device.delay(2)
            screen = self.set.save_fail_img_adv()
            if not self.set.device(resourceId="com.android.dialer:id/dialpad_floating_action_button").exists:
                self.tel.logger.info("FAIL: Quit dialer to another application")
                self.set.save_fail_img()
                if self.set.device(text="OK").exists:
                    self.set.device(text="OK").click.wait()
                self.set.back_to_home()
                return screen
            else:
                self.set.logger.info("Pass")
                self.set.back_to_home()
                return screen
        except:
            self.set.save_fail_img()
            self.set.logger.info("exception")
            self.set.logger.warning(traceback.format_exc())
            if self.set.device(text="OK").exists:
                self.set.device(text="OK").click.wait()
            self.set.back_to_home()
            return "got exception, check your script"

    def check_should_none1(self, code_num):
        self.set.logger.info("try to check whether the %s is closed" % code_num)
        try:
            self.tel.dialer_secret_code(code_num)
            self.set.device.delay(1)
            screen = self.set.save_fail_img_adv()
            if self.set.device(resourceId="com.tct.dialer:id/dial_single_action_button").exists:
                return "PASS", screen
            else:
                self.set.back_to_home()
                return "FAIL", screen
        except:
            self.set.save_fail_img()
            self.set.logger.info("exception")
            self.set.logger.warning(traceback.format_exc())
            self.set.back_to_home()
            return "got exception, check your script"

    def check_should_none2(self, code_num):
        self.set.logger.info("try to check whether the %s is closed" % code_num)
        try:
            self.tel.dialer_secret_code(code_num)
            self.set.device.delay(2)
            screen = self.set.save_fail_img_adv()
            if self.set.device(text="Google Apps setting").exists or self.set.device(
                    text="All Google apps disabled").exists:
                return "FAIL", screen
            else:
                self.set.back_to_home()
                return "PASS", screen
        except:
            self.set.save_fail_img()
            self.set.logger.info("exception")
            self.set.logger.warning(traceback.format_exc())
            self.set.back_to_home()
            return "got exception, check your script"

    def check_svn_dialer(self):
        self.set.logger.info("try to get svn value from dialer")
        try:
            self.tel.dialer_secret_code("*#06#")
            self.set.device.delay(2)
            if self.set.device(text="IMEI").exists:
                svn_value = self.get_svn()
                # self.set.device(resourceId="android:id/button1").click()
                return svn_value
            else:
                self.set.logger.info("enter IMEI page fail")
                self.set.back_to_home()
                return False
        except:
            self.set.save_fail_img()
            self.set.logger.info("exception to get svn value")
            self.set.logger.warning(traceback.format_exc())
            self.set.back_to_home()
            return False

    def get_svn(self):
        svn_str = self.set.device(textContains="SVN")
        svn_value = svn_str.get_text()
        svn_value = svn_value.split("SVN:")[1].strip()
        self.tel.logger.info("get svn success, svn is " + str(svn_value))
        return svn_value

    def get_parameters_version(self):
        self.set.logger.info("try to get parameter version")
        try:
            parameter_dic = {}
            self.dial_secret_code("##782#")
            self.set.device.wait("idle")
            self.set.device.delay(2)
            self.set.device(textContains="DISPLAY THE PARAMETER VERSION").click.wait()
            self.set.device.delay(1)
            screen = self.set.save_fail_img_adv()
            parameter_dic["NV parameters"] = self.set.device(textContains='Parameters Ver :').get_text().split(":")[
                1].strip()
            parameter_dic["Wifi version"] = self.set.device(textContains='hw nv').get_text().split(":")[1].strip()
            parameter_dic["BT"] = self.set.device(textContains='BT version').get_text().split(":")[1].strip()
            parameter_dic["Audio"] = self.set.device(textContains='Audio version').get_text().split(":")[1].strip()

            self.set.logger.info(parameter_dic)
            alist = ['%s= %s' % (key, value) for key, value in parameter_dic.items()]
            ret = '<br />'.join(alist)

            return ret, screen
        except:
            self.set.save_fail_img()
            self.set.logger.info("exception to get parameter version")
            self.set.logger.warning(traceback.format_exc())
            return 'FAIL', 'got exception, check your script'

    def check_svn_settings(self):
        self.set.logger.info("try to get svn value from settings")
        try:
            self.set.enter_settings("System")
            self.set.device.wait("idle")
            self.set.device(text="About phone").click()
            if self.set.device(scrollable=True).exists:
                self.set.device(scrollable=True).scroll.vert.to(text="Status")
            self.set.device(text="Status").click()
            self.set.device(text="IMEI information").click()
            self.set.device.wait("idle")
            svn_title = self.set.device(textContains="IMEI SV")
            svn_value = svn_title.sibling(resourceId="android:id/summary").get_text()
            self.set.logger.info("get svn success, svn is " + str(svn_value))
            return svn_value
        except:
            self.set.save_fail_img()
            self.set.logger.info("exception to get svn value")
            self.set.logger.warning(traceback.format_exc())
            return False

    def check_app_list(self, *apps):
        exists_app = []
        self.set.logger.info("try to check whether these apps in APP List: %s" % str(apps))
        self.set.device(description="All Items").click.wait()
        self.set.device.delay(1)

        for i in range(len(apps)):
            print str(apps[i])
            if self.set.device(scrollable=True, description="All Apps Tab").scroll.vert.to(text=str(apps[i])):
                exists_app.append(str(apps[i]))
            print "scroll to begining"
            self.set.device(scrollable=True, description="All Apps Tab").scroll.vert.toBeginning()
            self.set.device(scrollable=True, description="All Apps Tab").scroll.vert.toBeginning()

        if len(exists_app) > 0:
            self.set.logger.info("FAIL: can find the apps %s in APP List" % str(exists_app))
            return exists_app
        return True

    def install_apk(self, apk_file):
        folder_path = os.path.dirname(os.path.abspath(__file__))
        apk_path = os.path.join(folder_path, "test_file", apk_file)
        if not os.path.exists(apk_path):
            self.set.logger.info("Can not find the APK file")
            return False
        cmd = "adb -s %s install -r %s" % (self.serinoM, apk_path)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        if ("Success" in stdout) or ("Success" in stderr):
            self.set.logger.info("install apk success")
            return True
        return False

    def check_app_exists(self, app_name):
        try:
            if self.check_app(app_name):
                status = "PASS"
            else:
                self.set.logger.info("the app %s exists" % str(app_name))
                status = "FAIL"
            screen = self.set.save_fail_img_adv()
            return status, screen
        except:
            self.set.logger.debug("exception")
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return "FAIL", "got exception, check your script"

    def check_app_not_exist(self, app_name):
        try:
            if self.check_app(app_name):
                status = "FAIL"
            else:
                self.set.logger.info("the app %s exists" % str(app_name))
                status = "PASS"
            screen = self.set.save_fail_img_adv()
            return status, screen
        except:
            self.set.logger.debug("exception")
            self.set.save_fail_img()
            self.set.logger.warning(traceback.format_exc())
            return "FAIL", "got exception, check your script"

    def check_app(self, app_name):
        self.set.back_to_home()
        self.set.device.wait("idle")
        self.set.enter_main_apps()
        self.set.device(resourceId="com.tcl.android.launcher:id/search_box_input").click()
        self.set.device(resourceId="com.tcl.android.launcher:id/search_view").set_text(app_name)
        if self.set.device(textContains="Nothing locally found ").ext5:
            self.set.logger.info("the app %s not exists" % str(app_name))
            return False
        elif self.set.device(text=app_name,resourceId="com.tcl.android.launcher:id/app_name").ext5:
            self.set.logger.info("the app %s exists" % str(app_name))
            return True

    def long_press_power(self, sleep_time):
        self.set.adb.shell2("sendevent /dev/input/event3 1 116 1")
        time.sleep(0.1)
        self.set.adb.shell2("sendevent /dev/input/event3 0 0 0")
        time.sleep(sleep_time)
        self.set.adb.shell2("sendevent /dev/input/event3 1 116 0")
        time.sleep(0.1)
        self.set.adb.shell2("sendevent /dev/input/event3 0 0 0")
        time.sleep(1)

    def case_model_001(self):
        """
        take photo
        :return:
        """
        try:
            self.tel.dialer_secret_code("*#837837#")
            self.set.device.delay(2)
            screenshot = self.set.save_fail_img_adv()
            start_index = 'Product name:'
            end_index = 'Software version'
            version_info = self.set.device(textStartsWith=start_index).get_text()
            print "version_info:",version_info
            model = version_info[version_info.find(start_index) + len(start_index):version_info.find(end_index)]
            self.set.device(resourceId="android:id/button1").click()
            ret = model if len(model) > 0 else 'Check screenshot'
            return ret.strip(), screenshot
        except:
            self.set.logger.warning(traceback.format_exc())
            self.set.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_svn_001(self):
        try:
            self.set.logger.info("test_SVN_001 SVN")

            # Get SVN value from dialer
            _svn_dialer = self.check_svn_dialer()
            screenshot = self.set.save_fail_img_adv()
            # click OK to exist secured code input
            if self.set.device(resourceId="android:id/button1").exists:
                self.set.device(resourceId="android:id/button1").click()

            # Get SVN value from settings
            _svn_settings = self.check_svn_settings()
            screenshot += self.set.save_fail_img_adv()

            if _svn_dialer != _svn_settings:
                return 'FAIL', screenshot
            else:
                return _svn_settings, screenshot
        except:
            self.set.logger.warning(traceback.format_exc())
            self.set.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_hidden_code_006(self):
        try:
            self.set.logger.info("case_hidden_code_006, *#2886#_Version Information")
            for loop in range(3):
                self.tel.dialer_secret_code('*#2886#')
                if self.set.device(text="MOBILE PHONES").wait.exists():
                    break
            else:
                return

            self.set.device(text="MANU").click.wait()
            firmware = 'Firmware'
            firmware_btn = self.set.device(text=firmware)
            self.set.device(scrollable=True).scroll.vert.to(text=firmware)
            firmware_btn.click.wait()
            self.set.device.delay()

            assert self.set.device(text=firmware.upper()).wait.exists(), "**** %s activity do not start ****" % firmware
            screen = self.set.save_fail_img_adv()
            org_info = self.set.device(resourceId="com.android.mmi:id/textview_common_message").get_text()
            ret = self._generate_firmware_info(org_info)

            self.set.device.press.back()
            self.set.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)
            self.set.device(text="Exit").click()
            assert self.set.device(resourceId="com.tct.dialer:id/dial_single_action_button").wait.exists(), \
                "**** back from MMI test failed ****"
            # print ret
            return ret, screen
        except:
            self.set.logger.warning(traceback.format_exc())
            self.set.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def _generate_firmware_info(self, org_info):
        self.set.logger.info("process string '%s'" % org_info)
        alist = ['CKB Build ID', 'CKB Config ID', 'NFC']
        astr = org_info
        for item in alist:
            if item in astr:
                astr = astr.replace(item, '<br />%s' % item)
        return astr

    def case_app_check_006(self):
        try:
            support_center = 'Support Center'
            self.set.logger.info("case_hidden_code_006, verify support center exists or not")
            return self.check_app_exists(support_center)
        except:
            self.set.logger.warning(traceback.format_exc())
            self.set.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def case_settings_004(self):
        try:
            self.set.logger.info("case_hidden_code_006, verify navigation gesture from developer option")

            self.set.search_in_settings('navigation')
            screen = self.set.save_fail_img_adv()
            ret = 'FAIL'
            if self.set.device(text="No results").wait.exists(timeout=3000):
                ret = 'PASS'
            return ret, screen
        except:
            self.set.logger.warning(traceback.format_exc())
            self.set.save_fail_img()
            return 'FAIL', "got exception, check your script"

    def is_in_package_list(self, tar_package):
        self.set.logger.info("verify %s is in package list or not" % tar_package)
        packages = self.set.adb.shell('pm list packages')
        if tar_package in packages:
            return True
        else:
            return False

    def _get_name(self, csv_loc):
        names = os.listdir(csv_loc)
        if len(names) > 0:
            return max(names)
        return None

    def xxxtest_Debug_Property_001(self):
        """
        Debug Property_001
        QXDM_Crash Check
        :return:
        """
        self.set.logger.debug("test_Debug_Property_001 QXDM_Crash Check")
        ret = 'Manual Test'
        self.set_result(case_id='Debug Property_001', ret=ret)

if __name__ == "__main__":
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(SettingRelated)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
    # org_info = 'TP:  A5CKB Build ID: 2739303CKB Config ID: 0x00000014NFC: 120'
    # alist = ['TP', 'CKB Build ID', 'CKB Config ID', 'NFC']
    # astr = org_info
    # for item in alist:
    #     if item in astr:
    #         astr = astr.replace(item, '<br />%s'%item)
    # print astr
