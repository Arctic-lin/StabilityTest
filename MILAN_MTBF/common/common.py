# -*- coding: utf-8 -*-
from __future__ import division

import os
import subprocess
import sys
import time
import traceback
import uuid
import xmlrpclib
from datetime import datetime
from xml.dom.minidom import Document
from xml.etree.ElementTree import ElementTree, Element

from log_utils import create_folder

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
next_reg = r'(?i)^next'

if not sys.version_info < (2, 7, 9):
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

if not lib_path in sys.path:
    sys.path.append(lib_path)
from automator.uiautomator import Device
from configs import GetConfigs, Configs
import random
from configs import AppConfig
import log_utils

logger = log_utils.createlogger("COMMON")


def connect_device(device_name):
    """connect_device(device_id) -> Device
    Connect a device according to device ID.
    """
    environ = os.environ
    device_id = environ.get(device_name)
    if not device_id:
        device_id = device_name
    backend = Configs("common").get("backend", "Info")
    logger.debug("Device ID is " + device_id + " backend is " + backend)
    if backend.upper() == "MONKEY":

        device = globals()["%sUser" % backend](device_id)
    else:
        device = Device(device_id)
    if device is None:
        logger.critical("Cannot connect device.")
        raise RuntimeError("Cannot connect %s device." % device_id)
    return device


class Common(object):
    """Provide common functions for all scripts."""

    def __init__(self, device, mod, sdevice=None, timeout=5000):
        self.config = GetConfigs("common")
        self.config_smoke = GetConfigs("Smoke")
        self.config_mp = GetConfigs("mp_checklist")
        self.appconfig = AppConfig("appinfo")
        self.appconfig.set_section(mod)
        self.sdevice_tel = ""
        self.sdevice_msg = ""
        self.timeout = timeout
        if isinstance(device, Device):
            self.device = device
        else:
            self.mdevice_id = device
            self.device = connect_device(self.mdevice_id)
        if sdevice == None:
            pass
        elif isinstance(sdevice, Device):
            self.sdevice = sdevice
        else:  # sdevice_id
            self.sdevice = connect_device(sdevice)

        self.adb = self.device.server.adb
        self.project_name = self.config.get("ProductName", self.get_project_name().lower())
        self.isMILAN_GL = (self.project_name == "Milan_5061U_GL")
        self.isMILAN_EEA = (self.project_name == "Milan_5061U_EEA")
        self.is_testing_in_china = self.config.site == "CHINA"
        self.logger = log_utils.createlogger(mod)
        self.log_path = create_folder()

        if sdevice != None:
            if sdevice == "SDEVICE":
                self.sdevice_tel, self.sdevice_msg = self.get_tel_number(os.environ.get(sdevice))
            elif not isinstance(sdevice, Device):
                self.sdevice_tel, self.sdevice_msg = self.get_tel_number(sdevice)

    def get_tel_number(self, sdevice_id):
        sdevice_tel = ""
        sdevice_msg = ""
        _dict1 = self.config.commonconfig.items("Telephony")
        for key, value in _dict1:
            if key == sdevice_id:
                sdevice_tel = value

        _dict2 = self.config.commonconfig.items("Message")
        for key, value in _dict2:
            if key == sdevice_id:
                sdevice_msg = value
        return sdevice_tel, sdevice_msg

    def setup(self):
        music_files = os.path.join(self.project_root(), 'StabilityResource')
        self.logger.info('push media files to device')
        self.adb.cmd('push', music_files, '/sdcard')

    def get_project_name(self):
        return self.adb.shell("getprop ro.product.name").strip()

    def device(self):
        return self.device

    def sdevice(self):
        return self.sdevice

    def save_fail_img(self, newimg=None):
        """save fail image to log path.
        argv: The picture want to save as failed image.
        """
        pic_name = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        path = os.path.join(self.log_path, 'fail_img', pic_name + '.png')
        if os.path.exists(path):
            pic_name = pic_name + "_s"
            path = os.path.join(self.log_path, 'fail_img', pic_name + '.png')
        if newimg is None:
            self.logger.debug("Take snapshot.")
            newimg = self._screenshot(path)
        if newimg is None:
            self.logger.warning("newimg is None.")
            return False
        self.logger.error("Fail: %s" % (path))
        return True

    def save_fail_img_adv(self, newimg=None, pic_width='216', pic_height='324'):
        """save fail image to log path.
        argv: The picture want to save as failed image.
        """
        pic_name = self.screenshot_name()
        temp = "\\fail_img\\" + pic_name
        path = os.path.join(self.log_path, 'fail_img', pic_name)
        if newimg is None:
            self.logger.debug("Take snapshot.")
            newimg = self._screenshot(path)
        if newimg is None:
            self.logger.warning("newimg is None.")
            return False
        self.logger.error("Fail: %s" % (path))
        return '<img src=".%s" alt="get screeshot failed" width=%s height=%s>&nbsp;&nbsp;&nbsp;&nbsp;' % (
            temp, pic_width, pic_height)
        # return '.%s' % temp

    def save_fail_img_s(self, newimg=None):
        """save fail image to log path.
        argv: The picture want to save as failed image.
        """
        path = os.path.join(self.log_path, self.screenshot_name())
        if newimg is None:
            self.logger.debug("s-device Take snapshot.")
            newimg = self._screenshot(path)
        if newimg is None:
            self.logger.warning("newimg is None.")
            return False
        self.logger.error("Fail: %s" % (path))
        return True

    def _screenshot(self, out, suffix=''):
        remote_pic_path = '/sdcard/{}{}.png'.format(uuid.uuid4(), suffix)
        self.adb.shell('screencap', '-p', remote_pic_path)
        self.adb.cmd('pull', remote_pic_path, out)
        self.adb.shell('rm', remote_pic_path)
        return out

    def screenshot(self):
        pic_name = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        remote_pic_path = '/sdcard/Pictures/Screenshots/{}{}.png'.format(uuid.uuid4(), pic_name)
        self.adb.shell('screencap', '-p', remote_pic_path)

    def screenrecord(self):
        pic_name = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        remote_pic_path = '/sdcard/Pictures/Screenshots/{}{}.mp4'.format(uuid.uuid4(), pic_name)
        self.adb.shell('screenrecord', '--time-limit', '10', remote_pic_path)


    def get_file_num(self, path, format):
        """get number of file with specified format.
        """
        content = self.adb.shell("ls " + path + "/*" + format)

        # we change the return about shell method, change to string from list,
        if isinstance(content, str):
            # print content
            # will return "ls: /sdcard/DCIM/Camera//*.jpg: No such file or directory" if no pic
            # we should make sure the path is correct, otherwise the num always return 0
            num = 0 if "No such file or directory" in content else len(content.splitlines())
        else:
            return len(content)

        self.logger.debug("%s file num is %d." % (format, num))
        return num

    def start_activity(self, packet, activity):
        data = self.device.server.adb.shell("am start -n %s/%s" % (packet, activity))
        if data.find("Error") > -1:
            self.logger.error("Fail: %s/%s" % (packet, activity))
            return False
        return True

    def stop_app(self, package):
        data = self.device.server.adb.shell('am force-stop {}'.format(package))
        if data.find('Error') > -1:
            self.logger.error('force stop {} failed'.format(package))
            return False
        return True

    def start_app(self, name, b_desk=True):
        """start app
        arg: name(str) app name
             b_desk(Boolean) whether to start on the desktop
        """
        try:
            self.logger.debug("start app:%s" % name)
            if not self.device(resourceId="com.tcl.android.launcher:id/workspace",
                               packageName="com.tcl.android.launcher").exists:#不在主界面，执行back to home操作
                self.back_to_home()

            # 1, try to start from launcher home screen by text/description
            try_items = [self.device(text=name), self.device(description=name)]
            if b_desk:
                for item in try_items:
                    if item.exists:
                        item.click.wait()
                        self.logger.debug("app %s clicked by b_desk_1" % name)
                        return True
                else:
                    self.enter_main_apps()
                    self.swipe_vert_to_item_by_text(name, 363, 1346, 363, 445)
                    return True
            # 2, try to start from main apps
            else:
                for item in try_items:
                    self.enter_main_apps()
                    self.swipe_vert_to_item_by_text(name, 363, 1346, 363, 445)
                    return True

        except Exception as e:
            self.logger.warning(traceback.format_exc())
            self.logger.debug("enter app %s failed" % name)
            self.save_fail_img()
            return False

    def setup_language(self, deviceType):
        self.logger.debug("starting to setup %s language" % deviceType)
        if deviceType.lower() == "mdevice":
            device = self.device
        elif deviceType.lower() == "sdevice":
            device = self.sdevice

        while device(resourceId="com.android.stk:id/button_ok").exists:
            device(resourceId="com.android.stk:id/button_ok").click.wait()
            device.delay(2)
        device.click(533, 813)
        device.delay(2)
        if not device(scrollable=True).exists:
            device.click(533, 690)  # click language list
            device.wait("idle")
        device.wait("idle")
        device(scrollable=True).scroll.vert.to(text="English")
        device(text="English").click.wait()
        device.wait("idle")
        device(scrollable=True).scroll.vert.to(text="United States")
        device(text="United States").click.wait()
        if device(text="ENGLISH (UNITED STATES)").wait.exists():
            self.logger.debug("setup language successfully")
            return True
        self.logger.debug("setup language failed")
        self.save_fail_img()
        return False

    def through_oobe(self, deviceType, *gmail, **wifi_info):
        try:
            self.logger.debug("starting to through %s oobe" % deviceType)
            nothanks_reg = r'(?i)^no, thanks'

            if deviceType.lower() == "mdevice":
                device = self.device
            elif deviceType.lower() == "sdevice":
                device = self.sdevice

            if device(text="START").wait.exists(timeout=10000):
                device(text="START").click.wait()

            if device(text="SKIP").exists:
                self.logger.debug("skip connect to mobile network")
                device(text="SKIP").click.wait()

            if device(text="Set up as new").ext5:
                self.logger.debug("Set up as new")
                device(text="Set up as new").click.wait()

            if not self.connect_setupwizard_wifi(deviceType, **wifi_info) == "Account added":
                if device(text="OK").ext5:
                    device(text="OK").click()

                # ##不用assert的原因是，如果第二次重过oobe,已经添加了google账号的情况下不会再显示"Email or phone" 界面
                # if device(text="Email or phone").wait.exists(timeout=60000):
                if device(resourceId="identifierId", className="android.widget.EditText").wait.exists(timeout=60000):
                    device.wait("idle")
                    self.logger.debug("input account %s" % gmail[0])
                    device(resourceId="identifierId", className="android.widget.EditText").set_text(gmail[0])
                    if device(textMatches=next_reg).ext5:
                        device(textMatches=next_reg).click.wait()

                    device.dump()
                    if device(className="android.widget.EditText").wait.exists(timeout=30000):
                        device(className="android.widget.EditText").click()
                        device.dump()
                        time.sleep(3)
                        device(className="android.widget.EditText").set_text(gmail[1])
                        # self.adb.shell("input text %s"%gmail[1])
                        self.logger.debug("input password %s" % gmail[1])
                else:
                    self.logger.debug(
                        "'Email or phone' not exists ,maybe the first time already add successfully,so click the next button")
                    if device(textMatches=next_reg).ext5:
                        device(textMatches=next_reg).click.wait()

                if device(textMatches=next_reg).ext5:
                    device(textMatches=next_reg).click.wait()
                self.logger.debug("login google with %s" % gmail[0])

            if device(text="I agree").ext5:
                device(text="I agree").click.wait()

            # #为了检测ADD PREVIOUS ACCOUNT 特意做的处理，可以最快的速度点击ADD PREVIOUS ACCOUNT，
            for loop in range(8):
                self.logger.debug("check 'Unlock with fingerprint' %d times" % loop)
                if device(text="Unlock with fingerprint").ext5:
                    if device(text="SKIP").exists and device(
                            resourceId="com.android.settings:id/fingerprint_cancel_button").ext5:
                        device(text="SKIP").click.wait()
                        self.logger.debug("SKIP 'Unlock with fingerprint'")
                        break
                if device(text="I AGREE").wait.exists(timeout=2000):
                    device(text="I AGREE").click.wait()
                elif device(text="ADD PREVIOUS ACCOUNT").wait.exists(timeout=2000):
                    device(text="ADD PREVIOUS ACCOUNT").click.wait()

            else:
                assert device(text="Unlock with fingerprint").wait.exists(
                    timeout=5000), "fail to enter 'Unlock with fingerprint' page"

            if device(text="SKIP").ext5 and device(text="Set a screen lock").ext5:
                device(text="SKIP").click.wait()
                self.logger.debug("SKIP 'Set a screen lock'")
                if device(text="SKIP ANYWAY").ext5:
                    device(text="SKIP ANYWAY").click.wait()
            self.logger.debug("checking...")

            if device(text="CONTINUE").wait.exists(timeout=2000):
                device(text="CONTINUE").click.wait()

            # if device(text="Meet your Google Assistant").wait.exists(timeout=15000):
            #     if device(textMatches=next_reg).ext5:
            #         device(textMatches=next_reg).click.wait()
            #     self.logger.debug("SKIP 'Meet your Google Assistant'")
            # else:
            #     self.logger.debug("can not found 'Meet your Google Assistant'")
            #     for loop in range(5):
            #         if device(text="NEXT").exists:
            #             device(text="NEXT").click()
            #             self.logger.debug("found NEXT")
            #             break
            #         elif device(resourceId="com.google.android.googlequicksearchbox:id/opa_error_action_button").exists:
            #             device(resourceId="com.google.android.googlequicksearchbox:id/opa_error_action_button").click()
            #             self.logger.debug("found com.google.android.googlequicksearchbox:id/opa_error_action_button")
            #             break
            #         self.logger.debug("dump device ,and search NEXT again")
            #         self.device.dump()
            #     else:
            #         self.logger.debug("can not found NEXT,click 900,1520")
            #         device.click(900, 1520)
            #         time.sleep(2)

            device.dump()
            if device(text="Access your Assistant with Voice Match").wait.exists(timeout=15000):
                if device(text="NO THANKS").ext5:
                    self.logger.debug("click 'NO THANKS'")
                    device(text="NO THANKS").click()
                self.logger.debug("skip 'Access your Assistant with Voice Match'")
            else:
                self.logger.debug("not found  'Access your Assistant with Voice Match'")

            device.dump()
            if device(text="NO THANKS").ext5:
                self.logger.debug("click NO THANKS")
                device(text="NO THANKS").click()
            elif device(resourceId="com.google.android.googlequicksearchbox:id/opa_error_cancel_button").ext5:
                device(resourceId="com.google.android.googlequicksearchbox:id/opa_error_cancel_button").click()

            if device(text="SKIP").exists:
                device(text="SKIP").click()
            if device(textMatches=next_reg).exists:
                device(textMatches=next_reg).click()

            if device(textMatches=nothanks_reg).ext5:
                self.logger.debug("click nothanks_reg")
                device(textMatches=nothanks_reg).click()
            if device(textMatches=next_reg).exists:
                self.logger.debug("click next_reg")
                device(textMatches=next_reg).click()

            assert device(text="Google Services").wait.exists(timeout=30000) or device(
                text="Google services").wait.exists(
                timeout=30000), "fail to enter Google Services page"

            for loop in range(5):
                if device(text="MORE", resourceId="com.google.android.gms:id/next_button").exists:
                    device(text="MORE", resourceId="com.google.android.gms:id/next_button").click.wait()
                    continue
                if device(textContains="ACCEPT", resourceId="com.google.android.gms:id/next_button").exists:
                    device(textContains="ACCEPT", resourceId="com.google.android.gms:id/next_button").click.wait()
                    break
            if device(text="NO THANKS").ext5:
                device(text="NO THANKS").click.wait()

            # assert device(text="Agreement").wait.exists(timeout=10000), "fail to enter agreement page"
            if device(textMatches=next_reg).ext5:
                self.logger.debug("I Agree Agreement")
                device(textMatches=next_reg).click.wait()
                if device(text="OK").ext5:
                    device(text="OK").click()

            if device(text="Policy").ext5:
                self.logger.debug(
                    "Help to improve your device by sending anonymous diagnostics and usage data. By selecting this checkbox you agree to our Privacy Policy")
                device(textMatches=next_reg).click.wait()

            if device(textMatches=next_reg).ext5:
                device(textMatches=next_reg).click.wait()

            if device(textMatches=next_reg).ext5:
                device(textMatches=next_reg).click.wait()

            if device(textMatches=next_reg).ext5:
                device(textMatches=next_reg).click.wait()

            if device(text="OK").ext5:
                device(text="OK").click()
                self.logger.debug("select ok at 'Diagnostics'")

            if device(textMatches=next_reg).ext5:
                device(textMatches=next_reg).click.wait()

            if device(text="Setup is complete.").ext5:
                device(text="FINISH").click.wait()
                self.logger.debug("Setup is complete.")

            # dismiss log collection
            device.press.home()
            device.delay(5)
            device.press.home()

            assert device(packageName="com.blackberry.blackberrylauncher").wait.exists(
                timeout=5000) or device(text="OK").exists, "can't enter launcher"
            self.logger.debug("Enter blackberry launcher successfully")
            return True
        except:
            self.save_fail_img()
            self.logger.warning(traceback.format_exc())
            self.logger.debug("fail to through oobe, change to command method")
        return False

    def back_to_setup_wizard_homepage(self):
        for loop in range(10):
            self.device.press.back()
            time.sleep(0.5)
        for loop in range(10):
            if self.device(resourceId="com.google.android.setupwizard:id/start").wait.exists():
                self.logger.debug("back to setup wizard homepage successfully")
                return True
            self.device.press.back()
            time.sleep(0.3)
        self.logger.debug("back to setup wizard homepage successfully")
        return False

    def enter_playstore(self, times=1):
        """enter play store.
        """
        for loop in range(times):
            self.logger.debug('enter play store %s times' % (loop + 1))
            if self.device(resourceId="com.android.vending:id/search_box_idle_text").wait.exists(timeout=self.timeout):
                return True
            self.start_app("Play Store")

            # it is slow when open first time
            self.device.wait.idle()
            self.device.delay(5)
            if not self.device(resourceId="com.android.vending:id/search_box_idle_text").wait.exists(
                    timeout=self.timeout):
                if self.device(text="ACCEPT").exists:
                    self.device(text="ACCEPT").click.wait(timeout=5000)
                else:
                    self.save_fail_img()
                    self.back_playstore_homepage()
            if self.device(resourceId="com.android.vending:id/search_box_idle_text").wait.exists(timeout=self.timeout):
                return True
            else:
                self.logger.warning('enter play store fail!')
                self.save_fail_img()
                return False

    def battery_status(self):
        output = self.adb.shell('dumpsys battery')
        self.logger.info('battery status: {}'.format(output))

    def back_playstore_homepage(self):
        '''back to play store main screen
        '''
        for loop in range(5):
            if self.device(description="Show navigation drawer").wait.exists(timeout=1000):
                return True
            self.device.press.back()
        self.logger.warning("Cannot back to main app")
        return False

    def download_apk(self, apk):
        self.logger.info("download and open apk %s" % apk)
        self.logger.info("search %s apk" % apk)
        self.device(resourceId="com.android.vending:id/search_box_idle_text").click.wait()
        self.device(resourceId="com.android.vending:id/search_box_text_input").set_text(apk)
        self.device.press.enter()

        if self.device(textContains=apk, resourceId="com.android.vending:id/li_title").wait.exists(timeout=20000):
            self.device(textContains=apk, resourceId="com.android.vending:id/li_title").click()
            self.device.delay(5)
            if self.device(text="UNINSTALL").exists:
                self.device(text="UNINSTALL").click()
                self.device(text="OK").click()
                self.device.delay(5)
            self.logger.debug("download and Install %s apk." % apk)
            self.device.wait.idle()
            if self.device(text="INSTALL").ext5:
                self.device(text="INSTALL").click.wait()
            if self.device(text="ACCEPT").exists:
                self.device(text="ACCEPT").click.wait()

            num = 0
            while not self.device(text="OPEN").exists:
                if num > 10:
                    self.device.press.back()
                    self.device.delay(1)
                    self.device(text=apk, resourceId="com.android.vending:id/li_title").click()
                    self.device.delay(1)
                    if not self.device(text="OPEN").exists:
                        self.logger.debug("Install %s apk success failed." % apk)
                        self.save_fail_img()
                        return False
                        # return False
                    else:
                        break
                self.device.delay(20)
                num += 1
            self.logger.debug("download and Install %s apk success." % apk)
            return True

    def get_app_names(self):
        """
        get app names
        :return:
        """
        self.logger.debug("get app names")
        if self.device(description="All Items").exists:
            self.device(description="All Items").click()
            self.device.delay(1)
            self.device(text="APPS").click()
            self.device.delay(1)
            self.device(scrollable=True,
                        resourceId="com.blackberry.blackberrylauncher:id/apps_view").scroll.vert.toBeginning()

            # select Classic
            if not self.device(text="Classic").wait.exists(timeout=3000):
                self.device(resourceId="com.blackberry.blackberrylauncher:id/appsort_spinner").click.wait()
                if self.device(text="Classic").wait.exists(timeout=3000):
                    self.device(text="Classic").click.wait()

            app_list = []
            while True:
                first_app = self.device(resourceId="com.blackberry.blackberrylauncher:id/title").get_text()
                app_num = self.device(resourceId="com.blackberry.blackberrylauncher:id/title").count
                for i in range(app_num):
                    try:
                        app_title = self.device(resourceId="com.blackberry.blackberrylauncher:id/apps_view"). \
                            child(index=i).child(resourceId="com.blackberry.blackberrylauncher:id/title").get_text()
                    except:
                        app_title = "unknown"
                        self.logger.debug("skip")
                    app_list.append(app_title)
                    self.device.wait("idle")

                self.device(resourceId="com.blackberry.blackberrylauncher:id/apps_view",
                            scrollable=True).scroll.vert.forward()
                if self.device(resourceId="com.blackberry.blackberrylauncher:id/title").get_text() == first_app:
                    break

            app_list = list(set(app_list))
            self.logger.debug("app_list:%s" % app_list)
            return app_list

    def back_to_all_apps(self):
        """back_to_all_apps.
        """
        # self.logger.debug("back to all apps")
        for loop in range(4):
            self.device.press.back()
            if self.device(text="exit").wait.exists(timeout=500):
                self.device(text="exit").click()
            elif self.device(text="Quit").wait.exists(timeout=500):
                self.device(text="Quit").click()
            if self.device(resourceId=self.appconfig.id("id_group_title", "MenuNavigation")).wait.exists(timeout=500):
                return True

    def start_all_app(self, num=3):
        '''Call/People/ALL APPS/Messaging/Browser'''
        self.logger.debug("start all app")
        if self.device(description="ALL APPS").exists:
            self.device(description="ALL APPS").click()
        elif self.device(description="Apps").exists:
            self.device(description="Apps").click()
            self.device().fling.horiz.toBeginning()
        self.device().fling.horiz.toBeginning()
        for loop in range(3):
            self.adb.shell("input swipe 500 350 500 1600")
        for i in range(num):
            for j in range(self.device(className="android.widget.TextView").count - 2):
                if self.device(resourceId="com.tcl.android.launcher:id/apps_customize_pane_content").child(
                        index=0).child(
                    index=i).exists:
                    self.device(resourceId="com.tcl.android.launcher:id/apps_customize_pane_content").child(
                        index=0).child(
                        index=i).child(index=j).click()
                    self.device(text="ALL APPS").wait.gone(timeout=20000)
                    self.back_to_all_apps()
            self.device().fling.horiz.forward()
        return False

    def select_menu_item(self, stritem):
        self.device.press.menu()
        self.device.delay(1)
        self.device(text=stritem).click()
        self.device.delay(2)

    def skip_intro(self):
        try:
            if self.device(text="SKIP INTRO").wait.exists(timeout=2000):
                self.device(text="SKIP INTRO").click()
                self.logger.debug("SKIP INTRO successfully")
                return True
            else:
                self.logger.debug("SKIP INTRO not exists")
                return False
        except:
            self.logger.warning(traceback.format_exc())

    def allow_steps(self):
        try:
            self.logger.debug("starting to click allow steps button")
            count = 1
            while self.device(resourceId="com.android.packageinstaller:id/dialog_container").wait.exists(timeout=3500):
                self.logger.debug("starting to click allow button")
                if self.device(text="ALLOW").exists:
                    self.device(text="ALLOW").click.wait()
                if self.device(resourceId="com.android.packageinstaller:id/permission_message").ext5:
                    permission_message = self.device(
                        resourceId="com.android.packageinstaller:id/permission_message").get_text()
                    self.logger.debug("'%s' successfully" % permission_message)
                count += 1
                if count > 7:
                    self.logger.debug("skip allow steps failed")
                    return False
                time.sleep(0.5)
            else:
                self.logger.debug("skip allow steps page not exists,do not need skip the allow steps")
                return True
            # self.logger.debug("skip allow steps successfully")
            # return True
        except:
            self.logger.warning(traceback.format_exc())

    def dismiss_sync(self):
        if self.device(text="Dismiss").exists:
            self.device(text="Dismiss").click()
            self.device.delay(1)

    def connect_setupwizard_wifi(self, deviceType, **wifi_info):
        self.logger.debug("try to connect  %s wifi" % deviceType)

        if deviceType.lower() == "mdevice":
            device = self.device
        elif deviceType.lower() == "sdevice":
            device = self.sdevice

        if device(text="Account added").wait.exists(timeout=15000):
            self.logger.debug("skip 'Account added'")
            if device(textMatches=next_reg).exists:
                device(textMatches=next_reg).click()
                return "Account added"
        else:
            self.logger.debug("can not found 'Account added'")

        if not device(text="See all Wi‑Fi networks").wait.exists():
            self.logger.debug("can not found See all Wi‑Fi networks")
            return False
        device(text="See all Wi‑Fi networks").click.wait()
        assert device(scrollable=True).wait.exists(), "cannot find scrollable view"
        device(scrollable=True).scroll.vert.to(text="Add new network")
        device(text="Add new network").click.wait()
        self.logger.debug("Input SSID/PWD/Security")
        assert device(resourceId="com.android.settings:id/ssid").wait.exists(), "fail to enter add network page"
        device(resourceId="com.android.settings:id/ssid").set_text(wifi_info["wifi_name"])
        self.logger.debug("Select security")
        device(resourceId="com.android.settings:id/security").click.wait()
        device(text=wifi_info["wifi_security"]).click.wait(timeout=2000)
        device.delay(1)
        device(resourceId="com.android.settings:id/password").set_text(wifi_info["wifi_pwd"])
        device.delay(2)
        device(text="SAVE").click.wait()

        if device(text="Connect to Wi‑Fi").wait.gone(timeout=20000):
            self.logger.debug("connect wifi successfully")
        else:
            if device(text="SKIP").ext5:
                device(text="SKIP").click()
            if device(text="CONTINUE").ext5:
                device(text="CONTINUE").click()

    def _is_connected(self, type, sim=1):
        temp_type = type
        if type == "ALL":
            temp_type = "LTE"
        for i in range(20):
            if True:#self.adb.get_data_service_state(sim=sim) == temp_type: #这个方法似乎不通用？？
                break
            self.device.delay(10)
        else:
            self.logger.warning("Cannot get %s service." % (type))
            self.save_fail_img()
            self.device.press.back()
            return False

        for i in range(5):
            if self.adb.get_data_connected_status():
                return True
            self.device.delay(5)
        else:
            self.logger.warning("Cannot connect %s data." % (type))
            self.save_fail_img()
            self.device.press.back()
            return False

    def switch_network(self, type=None):
        """switch network to specified type.
        argv: (str)type -- the type of network.
        """
        self.logger.debug("Switch network to %s." % (type))
        self.start_activity(self.appconfig("RadioInfo", "package"), self.appconfig("RadioInfo", "activity"))
        self.device.delay(2)
        network_type = self.appconfig("RadioInfo", type)
        self.device(scrollable=True).scroll.to(text=self.appconfig("RadioInfo", "set"))
        if self.device(resourceId=self.appconfig.id("RadioInfo", "id_network")).wait.exists(timeout=2000):
            self.device(resourceId=self.appconfig.id("RadioInfo", "id_network")).click()
        self.device(scrollable=True).scroll.to(text=network_type)
        self.device.delay(1)
        self.device(text=network_type).click()
        self._is_connected(type)
        self.back_to_home()

    def install_apk(self, apk):
        """
        Method to install APK by adb install -rt
        apk: the path of apk, such mpChecklist/test_file/test.apk
        :return:
        """
        print os.path.dirname(__file__)
        base_dir = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
        print base_dir
        print base_dir + os.sep + apk
        print self.adb.cmd("install", "-r", base_dir + os.sep + apk).wait()

    def wait_for_full_device_boot(self, device_id):
        sleep_time = 0
        fully_booted = 0
        max_boot_time = 5 * 60
        print "wait until find the device"
        while sleep_time < max_boot_time:
            cmd1 = "adb -s %s shell getprop service.bootanim.exit" % device_id
            cmd2 = "adb -s %s shell getprop dev.bootcomplete" % device_id
            animation = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
            booted = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
            if ("1" in animation) and ("1" in booted):
                fully_booted = 1
                time.sleep(5)
                break
            sleep_time += 10
            self.logger.debug("Sleeping 300s: %d" % (max_boot_time - sleep_time))
            time.sleep(10)
        self.logger.debug("Sleeping 30s after boot animation for other services to do work")
        time.sleep(30)
        return fully_booted

    def back_to_home(self):
        """back_to_home.
        """
        self.logger.debug("back to launcher homepage,back 4 times then press home")
        for loop in range(4):
            self.device.press.back()
            self.device.delay(0.5)
        self.device.press.home()

    def back_to_home_s(self):
        """back_to_home.
        """
        for loop in range(4):
            self.sdevice.press.back()
            self.sdevice.delay(1)
        self.sdevice.press.home()

    def is_playing_video(self):
        """check if video is playing or not.
        """
        data = self.device.server.adb.shell("dumpsys media.player")
        if not data:
            return None
        if "Client" in data:
            self.logger.debug("The video is playing now")
            return True
        else:
            self.logger.debug("The video is not playing.")
            return False

    def is_playing_music(self):
        """check if music is playing or not.
        """
        data = self.device.server.adb.shell("dumpsys media_session")
        if not data:
            return None
        if "state=PlaybackState {state=3" in data:
            self.logger.debug("The music is playing now")
            return True
        else:
            self.logger.debug("The music is not playing.")
            return False

    def is_playing_music2(self):
        """check if music is playing or not.
        """
        data, _ = self.device.server.adb.shell2("dumpsys media_session")
        # print data
        if not data:
            return None
        if "state=PlaybackState {state=3" in data:
            self.logger.debug("The music is playing now")
            return True
        else:
            self.logger.debug("The music is not playing.")
            return False

    def is_airplane_opened(self):
        """
        check airplane is opened or not
        :return:
        """
        data, _ = self.device.server.adb.shell2("settings get global airplane_mode_on")
        # print data
        if not data:
            return None
        if "1" in data:
            self.logger.debug("airplane is opened")
            return True
        elif "0" in data:
            self.logger.debug("airplane is closed")
            return False

    def clear_notification(self):
        self.logger.info("clear notification")
        el = self.device(resourceId='com.android.systemui:id/dismiss')
        if el.exists:
            el.click()
            return True
        self.device.open.notification()
        if self.device(text="CLEAR ALL").wait.exists(timeout=2000):
            self.device(text="CLEAR ALL").click()
            self.device.delay(1)
            return True
        if el.wait.exists(timeout=2000):
            el.click()
            self.device.delay(1)
            return True
        self.device.press.back()

    def clear(self, package):
        self.logger.info('clear {}'.format(package))
        self.adb.shell('pm', 'clear', package)

    def allow_permissions(self):
        try:
            el = self.device (textMatches='allow|ALLOW')
            while el.exists:
                el.click.wait()
                time.sleep(1)
        except:
            pass

    def back_end_call(self):
        """back to call page and end call
        """
        self.logger.info("starting to back to the call and end the call")
        self.device.press.home()
        self.device.open.notification()
        if self.device(text="HANG UP").ext5:
            self.device(text="HANG UP").click()
            self.logger.info("end the call successfully")
            return True

        self.logger.info("end the call failed")
        return False

    def exception_end_call(self):
        """when exception happened, m-device end the call
            try to close calls via UI again, if failed or got any exceptions, call API

        """
        if not self.adb.close_call_service():
            self.back_end_call()

    def random_name(self, index_num):
        numseed = "0123456789"
        sa = []
        for i in range(5):
            sa.append(random.choice(numseed))
        stamp = ''.join(sa)
        strname = 'Auto%02d' % (index_num + 1) + stamp   # todo: Benz can not match _
        logger.debug('Create a random name %s.' % strname)
        return strname

    def random_str(self, msg_stub=""):
        numseed = "abcdefg"
        sa = []
        for i in range(5):
            sa.append(random.choice(numseed))
        stamp = ''.join(sa)
        strname = msg_stub + stamp
        self.logger.debug('Create a random name %s.' % strname)
        return strname

    def clear_background(self):
        try:
            self.logger.info("clear the background")
            self.device.press.recent()
            self.device.delay(1)
            if self.device(resourceId="com.tcl.android.launcher:id/clearAll").exists:
                self.device(resourceId="com.tcl.android.launcher:id/clearAll").click()
                return
            elif self.device(className="android.widget.ImageButton").exists:
                self.device (className="android.widget.ImageButton").click()
                return
            if self.device(text="No recent items").exists:
                self.logger.info("No recent items")
                return
            if self.device(className='android.widget.Button').exists:
                self.device(className='android.widget.Button').click()
            self.device.press.home()
            assert False, "clear all background app failed"
        except:
            self.logger.debug(traceback.format_exc())

    def run_app_from_background(self, app):
        self.logger.info("run app: %s from background" % app)
        self.device.press.recent()
        for i in range(3):
            if self.device(text=app).wait.exists(timeout=3000):
                self.device(text=app).click.wait()
                self.device.delay(3)
                return True
            else:
                self.device.swipe(500, 230, 500, 1430, 100)
                self.device.delay(1)
        else:
            self.logger.info("app: %s not found in background" % app)
            return False

    def close_app_from_background(self, app):
        self.logger.info("close app: %s from background" % app)
        self.device.press.recent()
        for i in range(3):
            if self.device(description="Dismiss %s." % app).wait.exists(timeout=3000):
                self.device(description="Dismiss %s." % app).click.wait()
                assert not self.device(description="Dismiss %s." % app).wait.exists(
                    timeout=3000), "***** close app: %s failed" % app
                return True
            else:
                self.device.swipe(500, 230, 500, 1430, 100)
                self.device.delay(1)
        else:
            self.logger.info("app: %s not found in background" % app)
            return False

    def charging_full(self, critical=20):
        if self._get_battery_level() < critical:
            self.logger.info("battery is less than %s, start charging to full" % critical)
            self.device.sleep()
            while True:
                if self._get_battery_level() == 100:
                    self.logger.info("battery is full")
                    self.device.wakeup()
                    self.device.delay(1)
                    self.device.swipe(720, 2000, 807, 600, 50)
                    return True
                else:
                    self.device.delay(600)

    def wakeup(self):
        self.device.wakeup()
        self.device.delay(2)
        self.device.swipe(720, 2000, 807, 600, 50)

    def charging_full2(self):
        should_charge_full = self.config.get('TestCase', 'should_charge_full') == 'True'
        if not should_charge_full:
            return
        critical = int(self.config.get('TestCase', 'start_charge_level'))
        self.charging_full(critical)

    def _get_battery_level(self):
        battery_info = self.adb.shell('dumpsys battery').split()
        battery_level = 100
        for idx, item in enumerate(battery_info):
            if item == 'level:':
                battery_level = int(battery_info[idx + 1])
        return battery_level

    def set_mp_result(self, _result, test_case, testdata="", testtype=""):
        """
        :param _result: true of false, true:Pass, false:Fail
        :param test_case: case summary, it will be write into result file
        :param testdata: test data
        :return:
        """
        if _result is True:
            result = "PASS"
        elif _result is False:
            result = "FAIL"
        else:
            result = _result

        self.logger.info("%s: %s" % (test_case, result))

        # parse xml
        tree = ElementTree()
        tree.parse(self.result_file_path)
        root = tree.getroot()  # get root
        element = Element('testcase', {'casename': test_case, 'testresult': str(result), 'testdata': str(testdata),
                                       'testtype': str(testtype)})
        # element.tail = "\n\t"
        root.append(element)

        tree.write(self.result_file_path, encoding='utf-8', xml_declaration=True)

    def set_mp_result_to_template(self, data):
        """
        write result to template file directly
        :param ret: data should be a dict, {case name1: content1, case name2: content2}
        :param screenshots: should include html tags
        :return:
        """
        self.logger.debug("start updating result to template done, data=%s" % data)
        result_path = os.environ.get("LOG_PATH")
        if result_path is None:
            result_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        self.logger.debug("result_path:%s" % result_path)
        report = os.path.join(result_path, 'mpchecklist_new.html')
        lines = []
        with open(report) as template:
            lines = template.readlines()
            found_count = 0
            data_len = len(data.keys())
            for i, line in enumerate(lines):
                # self.logger.debug("line:%s" % line)
                if found_count < data_len:
                    for key, value in data.items():
                        # self.logger.debug("key:%s, value:%s" % (key, value))
                        if key in line:
                            lines[i] = line.replace(str(key), str(data.get(key)))
                            # self.logger.debug("%s" % (lines[i]))
                            found_count += 1

        with open(report, mode='w') as f_out:
            f_out.writelines(lines)
        self.logger.debug("updated result to template")

    def set_result(self, condition, test_case, failure_msg="", to_result=True):
        """

        :param condition: true of false
        :param test_case: case summery, it will be write into result file
        :param to_result: True, write into result, False, do not write into result, default is True
        :return:
        """

        result = "PASS" if condition else "FAIL"
        self.logger.info("%s: %s" % (test_case, result))

        # will not write to result file, if to_result is false
        if not to_result:
            return

        # parse xml
        tree = ElementTree()
        tree.parse(self.result_file_path)
        root = tree.getroot()  # get root
        element = Element('testcase',
                          {'casename': test_case, 'testresult': str(result)})  # create element testcase, attrib
        # element.tail = "\n\t"

        root.append(element)

        if not condition:  # add element only get fail
            failure = Element('failure', {'message': failure_msg})
            # failure.tail = "\n\t"
            element.append(failure)

        tree.write(self.result_file_path, encoding='utf-8', xml_declaration=True)

    def set_result_smoke(self, condition, test_case, auto_test=True, to_result=True):
        """
        set result to mp checklist or smoke
        :param condition:
        :param test_case:
        :param auto_test:
        :param to_result:
        :return:
        """
        result = "PASS" if condition else "FAIL"
        test_method = "Auto Test" if auto_test else "Manual Test"
        self.logger.info("%s: %s" % (test_case, result))

        # will not write to result file, if to_result is false
        if not to_result:
            return
        # parse xml
        tree = ElementTree()
        tree.parse(self.result_file_path_smoke)
        root = tree.getroot()  # get root
        element = Element('testcase', {
            'CaseID': test_case.split("_")[0],
            'CaseName': test_case.split("_")[1],
            'Checker': '',
            'TestResult': str(result),
            'DefectID': '',
            'Testmethod': test_method})  # create element testcase, attrib

        root.append(element)
        tree.write(self.result_file_path_smoke, encoding='utf-8', xml_declaration=True)

    def _write_date(self, test_case, to_result, pass_or_fail, failure_msg=""):
        self.logger.info("RESULT:%s,%s" % (test_case, pass_or_fail))
        if to_result:
            with open(self.result_file_path, "a") as result:
                result.write("%s,%s\n" % (test_case, pass_or_fail))
                if failure_msg:
                    result.write("failure message: %s \n")

    def create_xml_file(self, file_path):
        # self.logger.info("create result file: %s" % file_path)
        if os.path.exists(file_path):
            # self.logger.info("file exist, return")
            return
        # create document
        doc = Document()

        # create root testsuite
        testsuite = doc.createElement('testsuite')  # 创建根元素
        doc.appendChild(testsuite)

        with open(file_path, "w") as f:
            f.write(doc.toprettyxml(indent=''))

    def get_carrier_service_num(self):
        """
        get property [gsm.sim.operator.numeric]: [46002]
        1、中国联通的网络号：46001 46010
        2、中国电信的网络号：46003
        3、中国移动的网络号：46000 46002 46007
        :return:
        """
        carrier_service_num_mapping = {"10010": ["46001", "46010", "46009"],
                                       "10000": ["46003"],
                                       "10086": ["46000", "46002", "46007"]}
        sim_operator_numeric = self.adb.shell("getprop gsm.sim.operator.numeric").strip()
        self.logger.info("current sim operator numeric: %s." % sim_operator_numeric)
        for key, value in carrier_service_num_mapping.items():
            self.logger.debug("%s -> %s" % (key, value))
            if sim_operator_numeric in value:
                return key

        return None

    def time_task(self, start_time, seconds):
        end_time = time.time()
        print "end_time is %s", end_time
        duration = end_time - start_time
        print "duration is %s", duration
        if duration >= seconds:
            self.logger.debug("The time '%s' is over,return false,break the while circle" % seconds)
            return False
        else:
            self.logger.debug("The duration is %ss,less than %ss" % (duration, seconds))
            return True

    def get_prop(self, command):
        return self.adb.shell("getprop " + command).strip()

    def smoke_status_upload(self, status):
        try:
            project_info = {}
            product = self.get_prop("ro.product.device")
            print "product:", product
            subvarient = self.get_prop("ro.product.name")
            print subvarient
            software = self.get_prop("ro.build.display.id")
            print software
            branch = ""
            build = ""
            with open("C:\\%s\\url.txt" % self.project_name, "r", ) as f:
                url = f.read().strip()
                branch_list = url.split("/")
                branch = branch_list[-3]
                if branch == "SFI":
                    branch = "Master"
                elif "master" in branch:
                    branch = "Master"
                build = branch_list[-1].strip(".zip")

            pim_versions = self.get_pim_version()
            # print "pim_versions:",pim_versions
            project_info["product"] = product
            project_info["subvarient"] = subvarient
            project_info["software"] = software
            project_info["branch"] = branch
            project_info["status"] = status
            project_info["build"] = build
            project_info["pim"] = pim_versions
            print "upload project_info to tatserver:%s" % project_info
            server = xmlrpclib.ServerProxy("https://172.16.11.195:8000/tatserver/smoke/call/xmlrpc")
            # server = xmlrpclib.ServerProxy("http://127.0.0.1:8000/tatserver/smoke/call/xmlrpc")
            server.smoke_status_upload(project_info)
        except:
            self.logger.warning(traceback.format_exc())
            self.logger.debug("upload smoke test status Failed")
        self.logger.debug("upload smoke test status completed")

    def smoke_case_result_upload(self, case_name, test_result):
        try:
            case_info = {}
            case_id = case_name.split("_")[0]
            test_result = "Pass" if (test_result or test_result == "PASS") else "Failed"
            product = self.get_prop("ro.product.device")
            subvarient = self.get_prop("ro.product.name")
            software = self.get_prop("ro.build.display.id")
            case_info["product"] = product
            case_info["subvarient"] = subvarient
            case_info["software"] = software
            case_info["case_id"] = case_id
            case_info["test_result"] = test_result
            print "upload case_info to tatserver:%s" % case_info
            server = xmlrpclib.ServerProxy("https://172.16.11.195:8000/tatserver/smoke/call/xmlrpc")
            # server = xmlrpclib.ServerProxy("http://127.0.0.1:8000/tatserver/smoke/call/xmlrpc")
            server.smoke_case_result_upload(case_info)
        except:
            self.logger.warning(traceback.format_exc())
            self.logger.debug("upload smoke case test result Failed")
        self.logger.debug("upload smoke case test result completed")

    def get_pim_version(self):
        """
        get pim version
        :return:
        """
        # get packages and names to show
        target_packages = self.config.get_all_options("PIM")
        # print target_packages
        target_names = [self.config.get("PIM", option) for option in target_packages]
        # print target_names
        packages_mapping = {package: name for package, name in zip(target_packages, target_names)}
        print packages_mapping

        appversion = self.generate_all_app_versions_to_file()
        return self.get_app_versions(file_path=appversion, mapping=packages_mapping)

    def generate_all_app_versions_to_file(self):
        father_path = os.path.dirname(os.path.abspath(__file__))
        cmd = "dumpsys package packages"
        # temp_txt = "temp.txt"
        file_full_path = os.path.join(father_path, 'temp.txt')
        self.save_dump_to_file(cmd, file_full_path)
        # file_full_path = father_path + os.sep + temp_txt
        cmd2 = 'findstr /c \"Package [^{a-zA-Z] versionName=\" %s' % file_full_path
        print cmd2
        appversion = os.path.join(self.log_path, 'appversions.txt')
        self.save_cmd_to_file(cmd2, appversion)
        return appversion

    def save_dump_to_file(self, cmd, file):
        stdout, _ = self.adb.shell2(cmd)
        # print stdout
        with open(file, "wb") as pl:
            pl.writelines(stdout)

    def save_cmd_to_file(self, cmd, file):
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
        # print stdout
        with open(file, "wb") as pl:
            pl.writelines(stdout)

    def get_app_versions(self, file_path, mapping):
        file = open(file_path)
        app_version_dirc = {}
        while 1:
            line = file.readline()
            if not line:
                break
            if '[' in line:
                packageName = self.get_str_by(line, '[', ']')
                # print packageName
                for key in mapping.keys():
                    if key in line:
                        line = file.readline()
                        line = file.readline()
                        appVer = self.get_str_by(line, '=')
                        # print appVer
                        app_version_dirc[mapping.get(key)] = appVer
        print app_version_dirc
        return app_version_dirc

    def get_str_by(self, data, start_str, end_str='end'):
        start = data.find(start_str)
        if start >= 0:
            start += len(start_str)
            if end_str == 'end':
                end = -1
            end = data.find(end_str, start)
            return data[start:end].strip()

    def gen_loc_for_swipe(self, orientation=None, rate_from=None, rate_to=None, rate_2=0.5):
        """
        根据手机屏幕尺寸，生成2个坐标，用于左右，上下滑动
        usage: gen_loc_for_swipe(orientation='h', rate_from=0.1, rate_to=0.9, rate_2=0.5)
                水平方向滑动，屏幕高度的0.5倍，屏幕宽度的0.1倍到0.9倍，
        :param orientation: h or v
        :param rate_from: 屏幕宽度或高度的占比，起始点
        :param rate_to: 屏幕宽度或高度的占比，终点
        :param rate_2:  屏幕宽度或高度的占比
        :return: (x, y)
        """
        info = self.device.info
        display_width = info['displayWidth']
        display_height = info['displayHeight']
        self.logger.info(info)

        if orientation == 'h':
            sx = display_width * rate_from
            sy = display_height * rate_2
            ex = display_width * rate_to
            ey = sy
        elif orientation == 'v':
            sx = display_width * rate_2
            sy = display_height * rate_from
            ex = sy
            ey = display_height * rate_to
        else:
            raise AttributeError('orientation MUST be h or v')

        return sx, sy, ex, ey

    def set_screen_off_timeout(self, timeout=0):
        self.adb.shell('settings put system screen_off_timeout {}'.format(timeout))

    def disable_google_sync(self):
        self.start_app("Settings")
        self.device(scrollable=True).scroll.vert.to(text="Accounts")
        self.device(text="Accounts").click()
        if self.device(text="ON",resourceId="android:id/switch_widget").exists:
            self.device (text="ON", resourceId="android:id/switch_widget").click ()
            self.device(text="OK").click()
        self.device.press.back()
        self.device.press.back()
        self.device.press.home()

    def set_screenlock_none(self):
        self.start_app("Settings")
        self.device(scrollable=True).scroll.vert.to(text="Security")
        self.device(text="Security").click()
        self.device(text="Screen lock").click()
        self.device(text="None").click()
        self.device.press.home()
        self.device.delay()


    def gen_random_msg(self):
        s = '''In many cases classes can be turned into functions using closures
consider as an example the following class which allows a user to fetch URLs using a kind
of templating scheme'''
        return ','.join(random.sample(s.split(), 4))

    def gen_random_subject(self):
        s = ['fb', 'tw', 'wc', 'qq', 'lk', 'new']
        id = '1 2 3 4 5 6 7 8 9'
        ret = '[{}] - {}'.format(random.choice(s), ''.join(random.sample(id.split(), 5)))
        return ret

    def screenshot_name(self):
        '''
        :return: screent shot name of current time
        '''
        return '{}.png'.format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

    def project_root(self):
        '''

        :return: path of project root
        '''
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def enter_main_apps(self):
        self.logger.info("enter main apps")
        sx, sy, ex, ey = self.gen_loc_for_swipe(orientation='v', rate_from=0.8, rate_to=0.2)
        # print sx, sy, ex, ey
        self.device.swipe(sx, sy, ex, ey, steps=20)
        self.device.wait.idle()
        return self.is_in_main_apps()

    def is_in_main_apps(self):
        return self.device(resourceId="com.tcl.android.launcher:id/search_box_input").wait.exists()

    def scroll_vert_to_item_by_text(self, name):
        self.device(scrollable=True).scroll.vert.to(text=name)
        if self.device(text=name).wait.exists(timeout=10000):
            self.device(text=name).click()

    def swipe_vert_to_item_by_text(self, name, sx, sy, ex, ey, loops=5):
        for i in range(loops):
            if self.device(text=name).wait.exists(timeout=2000):
                self.device(text=name).click.wait()
                break
            self.device.swipe(sx, sy, ex, ey, steps=20)

    def click_if_exists_in_items(self, timeout, *items):
        """
        check item exist or not, if exist, click
        :param timeout:
        :param items:
        :return:
        """
        for item in items:
            if item.wait.exists(timeout=timeout):
                item.click()
                break

    def click_all_items_if_exists(self, timeout, *items):
        """
        check item exist or not, if exist, click
        :param timeout:
        :param items:
        :return:
        """
        for item in items:
            if item.wait.exists(timeout=timeout):
                item.click()

    def enable_wifi(self):
        adb_shell = "svc wifi enable"
        self.device.server.adb.shell(adb_shell)
        return True
    def disable_wifi(self):
        adb_shell="svc wifi disable"
        self.device.server.adb.shell(adb_shell)
        return True

    def disable_airplane(self):
        adb_shell = "settings put global airplane_mode_on 0"
        self.device.server.adb.shell(adb_shell)
        return True

    def enable_airplane(self):
        adb_shell = "settings put global airplane_mode_on 1"
        self.device.server.adb.shell(adb_shell)
        return True

    def enable_gps(self):
        adb_shell = "put secure location_providers_allowed +gps"
        self.device.server.adb.shell(adb_shell)
        return True

    def disable_gps(self):
        adb_shell = "put secure location_providers_allowed -gps"
        self.device.server.adb.shell(adb_shell)
        return True

    def click_text_DELETE(self):
        """
        try to click text DELETE, if can not found, click location
        :return:
        """
        # if self.device(text="DELETE").exists:
        #     self.device(text="DELETE").click()
        # else:
        #     x, y = 797, 2055
        #     self.device.click(x, y)
        self.logger.debug("click_text_DELETE start")
        x, y = 563, 1398
        self._click_and_log('DELETE', x, y)

    def click_text_CREATE(self):
        # if self.device(text="CREATE").exists:
        #     self.device(text="CREATE").click()
        # else:
        #     x, y = 797, 1304
        #     self.device.click(x, y)

        x, y = 518, 894
        self._click_and_log('CREATE', x, y)

    def click_text_SAVE(self):
        if self.isT1Q:
            x, y = 518, 894
        else:
            x, y = 518, 894
        self._click_and_log('SAVE', x, y)

    def click_text_ok(self):
        x, y = 797, 2055
        self._click_and_log('ok', x, y)

    def _click_and_log(self, text, x, y):
        self.logger.info("click {} location ({}, {})".format(text, x, y))
        self.device.click(x, y)

    def generate_bugreport(self):
        # self.save_fail_img()
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.logger.info("generate bugreport_{}".format(timestamp))
        cmd = '{}{}bugreport_{}.zip'.format(self.log_path, os.sep, timestamp)
        self.adb.bugreport(cmd)

    def sleep_if_power_low(self):
        timeout = 30*60
        try:
            batter_level = self.adb.batery_level_int()
            if batter_level is None:
                return
            elif batter_level <= 40:
                self.logger.info("batter is low, sleep until batter level >= 90")
                self.back_to_home()
                index = 1
                while True:
                    if self.adb.batery_level_int() >= 90:
                        break
                    self.logger.info("Sleep {}s - {}".format(timeout, index))
                    self.device.delay(timeout)  # 等待1小时
        except:
            pass

    def sleep_per_case(self):
        sleep_time = int(self.config.get("Sleep", 'sleep_time'))
        if sleep_time == 0:
            return
        self.logger.info("trun off screen and sleep {}s".format(sleep_time))
        self.device.sleep()
        self.device.delay(sleep_time)
        self.device.wakeup()

    def dump_hprof(self, package, key):
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.logger.info("dump hprof_{}".format(timestamp))
        cmd = 'am dumpheap {} /data/local/tmp/dumprmem_{}_{}.hprof'.format(package, key, timestamp)
        self.adb.shell(cmd)

    def print_meminfo(self):
        self.logger.info('*'*50)
        self.logger.info(self.adb.dumpsys_meminfo())
        self.logger.info('*'*50)

if __name__ == "__main__":
    a = Common("ed505a05", "Common")
    # a.start_app('Phone')
    a.generate_bugreport()
    # a.scroll_vert_to_item_by_text('Settings')
    # print a.get_file_num("/sdcard/DCIM/Camera/", ".jpg")
