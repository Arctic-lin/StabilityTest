#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
from __future__ import division

import os
import subprocess
import sys
import time
import traceback
import unittest

import common.log_utils

""" pre setup for MP chicklist
        skip setup wizard,
        connect wifi,
    send mail to notice test started
"""

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)
from common.settings import Settings, Wifi
from TclTools.MailHelper import MailHelper
from common import common


class PreSetUp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        serino_m = "MDEVICE"
        # serino_s = "SDEVICE"
        # serino_m = "5000002035"
        # serino_s = "1163817824"
        # serino_m = sys.argv[1]
        if "DEVICE" in serino_m:
            cls.m_device_id = os.environ.get(serino_m)
            # cls.s_device_id = os.environ.get(serino_s)
        else:
            cls.m_device_id = serino_m
            # cls.s_device_id = serino_s

        # init m device and some modules
        cls.settings = Settings(serino_m, "settings")
        cls.device = cls.settings.device
        cls.wifi = Wifi(cls.device, "wifi")
        cls.is_sprint = check_whether_sprint(cls.m_device_id)

        # get some infor from config file
        cls.wifi_name = cls.settings.config.getstr("wifi_name", "Wifi", "common")
        cls.wifi_pwd = cls.settings.config.getstr("wifi_password", "Wifi", "common")
        cls.wifi_security = cls.settings.config.getstr("wifi_security", "Wifi", "common")

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.settings.back_to_home()

    def test_1_prepare_m_device(self):
        """
            prepare m device for test:
            skip setup wizard, connect wifi, turn down display and sound
        """
        try:
            self.settings.logger.debug("m_device:skip setup wizard and dismiss tutorial ")
            prepare(self.m_device_id, self.settings, self.is_sprint)

            self.settings.logger.debug("m_device:connect wifi")
            self.conect_wifi(self.wifi)
            # self.settings.set_result(self.conect_wifi(self.wifi), "connect Wifi", to_result=False)

            self.settings.logger.debug("m_device:prepare mpchecklist.html")
            self.prepare_mpchecklist_html()

        except:
            self.settings.logger.warning(traceback.format_exc())
            self.settings.save_fail_img()

    def test_9_report_test_started(self):
        """
        sent email to inform test start
        :return:
        """
        mail = MailHelper()
        mail.mail_test_started()

    def conect_wifi(self, wifi):
        is_connect = wifi.connect_wifi(self.wifi_name, self.wifi_pwd, self.wifi_security)
        if wifi.device(text="Setup Wi-Fi Calling").wait.exists(timeout=30000):
            wifi.device(text="Don't show this message again").click.wait()
            wifi.device(text="SKIP").click.wait()
        # else:
        #     wifi.enter()
        #     wifi.close()
        #     wifi.open()
        #     if self.device(text="Setup Wi-Fi Calling").wait.exists(timeout=30000):
        #         self.device(text="Don't show this message again").click.wait()
        #         self.device(text="SKIP").click.wait()

        return is_connect

    def prepare_mpchecklist_html(self):
        # result_path = os.environ.get("LOG_PATH")
        # if result_path is None:
        #     result_path = os.path.dirname(os.path.dirname(__file__)) + "\\results"
        #
        # report = result_path + r"\mpchecklist.html"
        result_path = common.log_utils.create_folder()
        html_templates = os.path.dirname(os.path.dirname(__file__)) + "\\TclTools\\templates\\mpchecklist_new.html"
        html_result = result_path + "\\mpchecklist_new.html"
        lines = []
        with open(html_templates) as source:
            lines = source.readlines()
        with open(html_result, mode='w') as f:
            f.writelines(lines)


def process_setupwizard(settings, is_sprint, device_id):
    if settings.device(resourceId="com.blackberry.oobe:id/btn_next").wait.exists():
        setup_language(settings, is_sprint)
        try:
            through_oobe(settings)
        except:
            settings.save_fail_img()
            settings.logger.warning(traceback.format_exc())
            settings.logger.debug("fail to through oobe, change to command method")
            skip_wizard(device_id)
        wait_for_full_device_boot(settings, device_id)
        unlock_disable_sleep(device_id)
        time.sleep(5)

        # settings.device.click(300, 1100)
        settings.device.press.back()
        if settings.device(text="Select a Home app").wait.exists():
            settings.logger.debug("choose home app")
            settings.device(text="BlackBerry Launcher").click.wait()
            settings.device(text="ALWAYS").click.wait()
        time.sleep(5)
        settings.device.press.home()
        settings.device.delay()


def prepare(device_id, settings, is_sprint):
    # unlock_disable_sleep(device_id)
    # if settings.device(packageName="com.google.android.setupwizard").exists:
    #     # setup_language(settings, is_sprint)
    #     dismiss_launcher_tutorial(device_id)
    #     skip_wizard(device_id)
    #     wait_for_full_device_boot(settings, device_id)
    #     unlock_disable_sleep(device_id)
    #
    # close_verify_adb_installs(device_id)
    unlock_disable_sleep(device_id)
    if settings.adb.is_cn_variant():
        process_setupwizard(settings, is_sprint, device_id)

    dismiss_config(settings, is_sprint)
    settings.device.press.home()
    dismiss_launcher_tutorial(device_id)
    # grant_permission.start_test(device_id)


def through_oobe(settings, *gmail, **wifi_info):
    # Welcome activity, click let's go
    settings.device(text="LET'S GO").click.wait()

    # insert Sim card activity, click SKIP
    if settings.device(text="Insert SIM card").wait.exists(timeout=10000):
        settings.device(text="SKIP").click.wait()
        settings.device.delay()

    # Get Connected activity(wifi), click Don't use any network for setup
    # settings.device(text="Set up as new").click.wait()
    # connect_wifi(settings, **wifi_info)
    settings.device(scrollable=True).scroll.vert.to(text="Don’t use any network for setup")
    settings.device(text="Don’t use any network for setup").click.wait()
    settings.device(resourceId="android:id/button1").click.wait()

    if settings.device(text="Setup your BlackBerry account").wait.exists(timeout=10000):
        settings.device(text="SKIP").click.wait()
        settings.device.delay()

    # Date & time activity, click NEXT
    settings.device(text="NEXT").click.wait()
    settings.device.delay()

    # Name activity, click NEXT
    settings.device(text="NEXT").click.wait()
    settings.device.delay()

    # Nunlock with fingerprint activity, click SKIP
    if settings.device(text="SKIP").wait.exists():
        settings.device(text="SKIP").click.wait()
        settings.device.delay()

    # Agreement activity
    settings.device(text="NEXT").click.wait()
    settings.device.delay()

    # Insider Program activity, click No,not now, and SKIP
    settings.device(textContains="not now").click.wait()
    settings.device.delay()
    settings.device(text="SKIP").click.wait()
    settings.device.delay()

    settings.device(text="FINISH").click.wait()
    settings.device.delay()

    # dismiss log collection
    settings.device.press.home()
    settings.device.delay(5)
    settings.device.press.home()

    assert settings.device(packageName="com.blackberry.blackberrylauncher").wait.exists(
        timeout=5000), "can't enter launcher"


def dismiss_launcher_tutorial(device_id):
    print 'dismiss_launcher_tutorial start'
    command = "adb -s %s shell am broadcast -a com.blackberry.blackberrylauncher.EXIT_TUTORIAL -n com.blackberry." \
              "blackberrylauncher/com.blackberry.blackberrylauncher.ExitTutorialReceiver" % device_id
    subprocess.call(command)
    print 'dismiss_launcher_tutorial end'


def close_verify_adb_installs(device_id):
    print 'close_verify_adb_installs start'
    command = "adb -s %s shell settings put global verifier_verify_adb_installs 0" % device_id
    os.system(command)
    print 'close_verify_adb_installs end'


def reboot_device(device_id, settings, _is_sprint=False):
    settings.logger.debug("reboot device")
    os.system('adb -s %s reboot' % device_id)
    wait_for_full_device_boot(settings, device_id)
    unlock_disable_sleep(device_id)
    command = "adb -s %s shell settings put global verifier_verify_adb_installs 0" % device_id
    os.system(command)
    dismiss_config(settings, _is_sprint)

    # if _is_sprint:
    #     if settings.device(text="Configuring service").wait.exists(timeout=120000) and settings.device(text="SKIP").
    # wait.exists(timeout=300000):
    #         settings.device(text="exists").click.wait()
    #         if settings.device(text="CONTINUE").wait.exists(timeout=180000):
    #             settings.device(text="CONTINUE").click.wait()
    #     return settings.back_to_home()


def wait_for_full_device_boot(settings, device_id):
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
            # settings.logger.debug("reboot success")
            fully_booted = 1
            time.sleep(5)
            break
        # animation = settings.device.server.adb.shell('getprop service.bootanim.exit')
        # booted = settings.device.server.adb.shell('getprop dev.bootcomplete')
        # if ("1" in animation) and ("1" in booted):
        #     settings.logger.debug("reboot success")
        #     fully_booted = 1
        #     time.sleep(5)
        #     break
        sleep_time += 10
        if settings is not None:
            settings.logger.debug("Sleeping 300s: %d" % (max_boot_time - sleep_time))
        print "Sleeping 300s: %d" % (max_boot_time - sleep_time)
        time.sleep(10)
    # allow an additional minute after boot animation for other services to do work
    if settings is not None:
        settings.logger.debug("Sleeping 60s after boot animation for other services to do work")
    print "Sleeping 60s after boot animation for other services to do work"
    time.sleep(60)
    return fully_booted


def unlock_disable_sleep(device_id):
    os.system('adb -s %s shell svc power stayon true' % device_id)
    time.sleep(2)
    os.system('adb -s %s shell input keyevent KEYCODE_MENU' % device_id)


def push_files(device_id, settings):
    file_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "presetStability"
    cmd = "adb -s %s push %s /sdcard/Download/" % (device_id, file_path)
    settings.logger.debug(cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines, stderr = proc.communicate()
    proc.wait()
    # output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if "0 files skipped" in lines:
        settings.logger.debug("files push successful")
        return True
    settings.logger.debug("files push fail")
    settings.logger.debug(stderr)
    return False


def setup_language(settings, _is_sprint):
    settings.logger.debug("setup language")
    while settings.device(resourceId="com.android.stk:id/button_ok").exists:
        settings.device(resourceId="com.android.stk:id/button_ok").click.wait()
        settings.device.delay(2)

    if settings.device(text="ENGLISH (UNITED STATES)").wait.exists():
        settings.logger.debug("setup language success")
        return True

    settings.device(resourceId="com.blackberry.oobe:id/tv_language").click()
    settings.device.delay(2)
    # settings.device.click(533, 813)
    # settings.device.delay(2)
    if not settings.device(scrollable=True).exists:
        settings.device.click(525, 540)  # click language list
        settings.device.wait("idle")
    # if settings.device(resourceId="com.tct.setupwizard.overlay:id/language_spinner").wait.exists(timeout=10000):
    #     settings.device(resourceId="com.tct.setupwizard.overlay:id/language_spinner").click.wait()
    # elif settings.device(resourceId="com.google.android.setupwizard:id/language_picker").exists:
    #     settings.logger.debug("123123123123123123") "com.google.android.setupwizard:id/language_picker"
    #     settings.device(resourceId="com.google.android.setupwizard:id/language_picker").click.wait()
    # settings.device.wait("idle")
    # if settings.device(resourceId="com.tct.setupwizard.overlay:id/language_spinner").exists:
    #     settings.device(resourceId="com.tct.setupwizard.overlay:id/language_spinner").click.wait()
    # if settings.device(resourceId="com.google.android.setupwizard:id/language_picker").exists:
    #     settings.logger.debug("111111111")
    #     settings.device(resourceId="com.tct.setupwizard.overlay:id/language_spinner").click.wait()
    settings.device.wait("idle")
    if _is_sprint:
        settings.device(scrollable=True).scroll.vert.to(text="English (United States)")
        settings.device(text="English (United States)").click.wait()
    else:
        settings.device(scrollable=True).scroll.vert.to(text="English")
        settings.device(text="English").click.wait()
        settings.device.wait("idle")
        settings.device(scrollable=True).scroll.vert.to(text="United States")
        settings.device(text="United States").click.wait()
    if settings.device(text="English (United States)").wait.exists():
        settings.logger.debug("setup language success")
        return True

    settings.logger.debug("setup language fail")
    settings.save_fail_img()
    return False


def skip_wizard(device_id):
    print "skip setup wizard start"
    command1 = "adb -s %s shell settings put global device_provisioned 1" % device_id
    command2 = "adb -s %s shell settings put secure user_setup_complete 1" % device_id
    command3 = "adb -s %s reboot" % device_id
    os.system(command1)
    time.sleep(2)
    os.system(command2)
    time.sleep(2)
    os.system(command3)
    print "skip setup wizard end"


def dismiss_config(settings, _is_sprint):
    settings.logger.debug("try to dismiss configuring server page")
    if settings.device(resourceId="com.android.stk:id/button_ok").exists:
        settings.device(resourceId="com.android.stk:id/button_ok").click.wait()
    if not _is_sprint:
        settings.logger.debug("dismiss configuring server page success")
        return True
    if settings.device(packageName="com.redbend.app", text="Configuring service").wait.exists(timeout=120000) \
            or settings.device(packageName="com.sprint.ms.smf.services").wait.exists(timeout=60000):
        settings.logger.debug("delay 60s")
        settings.device.delay(60)
        settings.device.press.home()
        settings.device.wait("idle")
    if settings.device(packageName="com.blackberry.blackberrylauncher").wait.exists():
        settings.logger.debug("dismiss configuring server page success")
        return True
    else:
        settings.logger.debug("dismiss configuring server page FAIL!!!")
        settings.save_fail_img()
        return False


# ############################################## unused ################################################################
def dismiss_recorder_pop(settings):
    if not settings.start_app("Sound Recorder"):
        settings.logger.debug("fail to enter Recorder")
        settings.save_fail_img()
        return False
    settings.device.wait("idle")
    if settings.device(text="AGREE").wait.exists(timeout=5000):
        settings.device(text="AGREE").click.wait()
    if settings.device(resourceId="com.tct.soundrecorder.bb:id/recordButton").wait.exists():
        settings.logger.debug("setup Recorder success")
        return True
    settings.logger.debug("setup Recorder FAIL!!!")
    return False


def check_whether_sprint(device_id):
    cmd = "adb -s %s shell getprop ro.boot.binfo.subvariant" % device_id
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
    if output.strip() == "sprint":
        print "the device is sprint subvariant"
        return True
    return False


def dismiss_productivity_edge(settings):
    settings.logger.debug("start to setup Productivity Edge")
    try:
        for loop in range(7):
            settings.device.swipe(1070, 760, 220, 760, 20)
            if settings.device(text="SKIP INTRO").wait.exists():
                settings.device(text="SKIP INTRO").click.wait()
                time.sleep(2)
            for i in range(7):
                settings.device.wait("idle")
                if settings.device(text="ALLOW").exists:
                    settings.device(text="ALLOW").click.wait()
            if settings.device(resourceId="com.blackberry.productivityedge:id/tabIcon").wait.exists():
                settings.logger.debug("setup productivityEdge successfully.")
                return True
        settings.save_fail_img()
        settings.logger.debug("setup Productivity Edge failed.")
        return False
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()
        return False


def dismiss_dtek_welcome(settings):
    settings.logger.debug("start to setup DTEK")
    try:
        if not settings.start_app("DTEK by BlackBerry"):
            settings.logger.debug("fail to enter DTEK")
            settings.save_fail_img()
            return False
        if settings.device(text="SKIP").wait.exists():
            settings.device(text="SKIP").click.wait()
            time.sleep(2)
        for i in range(5):
            settings.device.wait("idle")
            if settings.device(text="ALLOW").exists:
                settings.device(text="ALLOW").click.wait()
        settings.device.wait("idle")
        if settings.device(text="Device security status").exists:
            settings.logger.debug("Dismiss DTEK's welcome page success")
            return True
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()
        return False


def dismiss_device_search_welcome(settings):
    settings.logger.debug("start to setup device search")
    try:
        if not settings.start_app("Device Search"):
            settings.logger.debug("fail to enter Device Search")
            settings.save_fail_img()
            return False
        if settings.device(text="SKIP INTRO").wait.exists():
            settings.device(text="SKIP INTRO").click.wait()
            time.sleep(2)
        for i in range(5):
            settings.device.wait("idle")
            if settings.device(text="ALLOW").exists:
                settings.device(text="ALLOW").click.wait()
        settings.device.wait("idle")
        if settings.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").exists:
            settings.logger.debug("Dismiss Device Search's welcome page success")
            return True
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()
        return False


def dismiss_map_welcome(settings):
    try:
        settings.logger.debug("start to setup map")
        enter_map_got_it(settings)
        settings.back_to_home()
        enter_map_got_it(settings)
        if not settings.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").exists:
            settings.logger.debug("fail to dismiss map's introduce page")
            settings.save_fail_img()
            return False
        settings.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").click.wait()
        settings.device(resourceId="com.google.android.apps.maps:id/search_omnibox_edit_text"). \
            set_text("university of nottingham ningbo")
        settings.device.press.enter()
        settings.device.wait("idle")
        if settings.device(text="DIRECTIONS").wait.exists(timeout=30000):
            settings.device(text="DIRECTIONS").click.wait()
            settings.device.delay(2)
            if settings.device(className="android.widget.Button", text="OK").exists:
                settings.device(className="android.widget.Button", text="OK").click.wait()
                settings.device.wait("idle")
            if settings.device(text="START").wait.exists(timeout=30000):
                settings.device(text="START").click.wait()
                if settings.device(text="GOT IT").wait.exists(timeout=3000):
                    settings.device(text="GOT IT").click.wait()
                    if settings.device(text="GOT IT").wait.gone(timeout=3000):
                        settings.logger.debug("dismiss map welcome page successfully")
                        return True
        settings.logger.debug("fail to dismiss map welcome page")
        settings.save_fail_img()
        return False
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()
        return False


def enter_map_got_it(_settings):
    if not _settings.start_app("Maps"):
        _settings.logger.debug("fail to enter Maps")
        _settings.save_fail_img()
        return False
    time.sleep(3)
    if _settings.device(text="GOT IT").exists:
        _settings.device(text="GOT IT").click.wait()
    if _settings.device(text="TURN OFF").exists:
        _settings.device(text="TURN OFF").click.wait()


def hub_email_setup(email):
    try:
        if not email.start_app("Hub"):
            email.logger.debug("fail to enter Hub")
            email.save_fail_img()
            return False
        email.device(description="Open navigation drawer").click.wait()
        email.device(text="Settings").click.wait()
        email.device(text="General Settings").click.wait()
        if email.device(className="android.widget.LinearLayout", index=4).child(index=1).child(checked=True):
            email.device(text="Conversation view").click.wait()
        if email.device(className="android.widget.LinearLayout", index=4).child(index=1).child(checked=True):
            email.save_fail_img()
            email.logger.debug("fail to un-check Conversation view")
        email.back_to_hub_home()
        return True
        # email.enter_box("Inbox")
        # if not email.device(description="Compose button").wait.exists():
        #     email.save_fail_img()
        #     email.logger.error("fail to disable ASK FOR PERMISSION pop up")
        # email.device(description="Compose button").click.wait()
        # if email.device(text="ASK FOR PERMISSION").wait.exists(timeout=5000):
        #     email.device(text="ASK FOR PERMISSION").click.wait()
        #     if email.device(text="ALLOW").exists:
        #         email.device(text="ALLOW").click.wait()
        # email.device(descriptionContains="Sent from").click.wait()
        # if email.device(text="ASK FOR PERMISSION").wait.exists(timeout=5000):
        #     email.device(text="ASK FOR PERMISSION").click.wait()
        #     if email.device(text="ALLOW").exists:
        #         email.device(text="ALLOW").click.wait()
        # email.back_to_hub_home()
    except:
        email.logger.warning(traceback.format_exc())
        email.save_fail_img()
        return False


def hub_add_gmail(email, account, pwd):
    try:
        email.logger.debug("enter hub to add gmail account")
        if not email.start_app("Hub"):
            email.logger.debug("fail to enter Hub")
            email.save_fail_img()
            return False
        email.device(description="Open navigation drawer").click.wait()
        email.device(text="Add account").click.wait()
        email.device(text="Email address").set_text(account)
        email.device.wait("idle")
        email.device(className="android.widget.Button", text="NEXT").click.wait()
        email.device.delay(timeout=20)
        if email.device(className="android.widget.Button", resourceId="next").wait.exists(timeout=20000):
            email.device(className="android.widget.Button", resourceId="next").click.wait()
            email.device.delay(2)
            if email.device(resourceId="Passwd").wait.exists(timeout=20000):
                email.device(resourceId="Passwd").set_text(pwd)
                email.device.wait("idle")
                email.device(resourceId="signIn").click.wait()
                if email.device(resourceId="submit_approve_access").wait.exists(timeout=20000):
                    for i in range(3):
                        email.device(resourceId="submit_approve_access").click.wait()
                        if not email.device(resourceId="submit_approve_access").exists:
                            break
                        email.device.delay(3)
                    if email.device(className="android.widget.Button", text="NEXT").wait.exists(timeout=20000):
                        email.device(className="android.widget.Button", text="NEXT").click.wait()
                        if email.device(className="android.widget.Button", text="DONE").wait.exists(timeout=20000):
                            email.device(className="android.widget.Button", text="DONE").click.wait()
                            email.device.wait("idle")
                            if email.device(description="Open navigation drawer").wait.exists(timeout=5000):
                                email.logger.debug("add account successful")
                                return True
        email.logger.debug("enter hub to add gmail account FAIL!!!")
    except:
        email.logger.warning(traceback.format_exc())
        email.logger.debug("enter hub to add gmail account exception!!!")
        email.save_fail_img()
        return False


def dismiss_hub_welcome(email, account, password):
    try:
        email.logger.debug("Enter Hub to cancel permission page")
        if not email.start_app("Hub"):
            email.logger.debug("fail to enter Hub")
            email.save_fail_img()
            return False

        if email.device(description="Open navigation drawer").wait.exists(timeout=5000):
            email.logger.debug("welcome screen dismissed")
            return True

        if email.device(description="NEXT").wait.exists(timeout=3000):
            email.device(description="NEXT").click.wait()
        if email.device(text="GRANT PERMISSIONS").wait.exists(timeout=5000):
            email.device(text="GRANT PERMISSIONS").click.wait()
        while email.device(text="ALLOW").exists:
            email.device(text="ALLOW").click.wait()
        if email.device(text="ADD ACCOUNT").exists:
            email.device(text="ADD ACCOUNT").click.wait()
        if email.device(text="ADD OTHER ACCOUNT").exists:
            email.device(text="ADD OTHER ACCOUNT").click.wait()
        email.device(text="Email address").set_text(account)
        email.device.wait("idle")
        email.device(text="MANUAL SETUP").click.wait()
        email.device(text="MICROSOFT EXCHANGE ACTIVESYNC").click.wait()
        email.device(resourceId="com.blackberry.infrastructure:id/password_edittext").set_text(password)
        email.device.wait("idle")
        # if not email.device(text="Server").exists:
        #     email.device.press.back()
        # email.device(description="Server").set_text("mail.tcl.com")
        # email.device.wait("idle")
        email.device(text="NEXT").click.wait()
        email.device(text="Remote security administration").wait.exists(timeout=60000)
        email.device(text="OK").click.wait()
        # email.device(resourceId="com.blackberry.infrastructure:id/account_email_sync_window").click.wait()
        # email.device(text="Forever").click.wait()
        # if email.device(text="Create a home screen shortcut", checked="true").exists:
        #     email.device(text="Create a home screen shortcut").click.wait()
        # if email.device(text="Sync contacts from this account", checked="true").exists:
        #     email.device(text="Sync contacts from this account").click.wait()
        # if email.device(text="Sync calendar from this account", checked="true").exists:
        #     email.device(text="Sync calendar from this account").click.wait()
        # email.device.swipe(570, 1630, 570, 680)
        # email.device.wait("idle")
        # if email.device(text="Sync tasks from this account", checked="true").exists:
        #     email.device(text="Sync tasks from this account").click.wait()
        # if email.device(text="Sync notes from this account", checked="true").exists:
        #     email.device(text="Sync notes from this account").click.wait()
        email.device(resourceId="com.blackberry.infrastructure:id/next").click.wait()

        if email.device(text="Security update").wait.exists(timeout=60000):
            email.device(text="OK").click.wait()
            if email.device(text="Exchange Device Admin").wait.exists(timeout=2000):
                email.device(scrollable=True).scroll.vert.toEnd(steps=10)
                email.device(text="Activate this device administrator").click.wait()
        email.device(resourceId="com.blackberry.infrastructure:id/next").click.wait()
        if email.device(resourceId="com.blackberry.hub:id/slidesOverlayButtonSkip").wait.exists(timeout=3000):
            email.device(resourceId="com.blackberry.hub:id/slidesOverlayButtonSkip").click.wait()
        if email.device(description="Open navigation drawer").wait.exists(timeout=5000):
            email.logger.debug("add account successful")
            return True
        email.logger.error("add account fail")
        email.save_fail_img()
        return False
    except:
        email.logger.warning(traceback.format_exc())
        email.save_fail_img()
        return False


def add_bookmarks(chrome):
    try:
        chrome.device(resourceId="com.android.chrome:id/menu_button").click.wait()
        chrome.device(text="Bookmarks").click.wait()
        if chrome.device(text="Sync your bookmarks").exists:
            chrome.device(text="NO THANKS").click.wait()
        if chrome.device(text="Carrier Bookmarks").exists:
            chrome.device(text="Carrier Bookmarks").sibling(resourceId="com.android.chrome:id/more").click.wait()
            chrome.device(text="Delete").click.wait()
        chrome.home()
        chrome.browser_webpage(website="sina.cn")
        if not chrome.save_bookmark(page=u"手机新浪网"):
            chrome.logger.error("fail to add bookmark - sina")
            chrome.save_fail_img()
        chrome.home()
        chrome.browser_webpage(website="qq.com")
        if not chrome.save_bookmark(page=u"腾讯网"):
            chrome.logger.error("fail to add bookmark - qq.com")
            chrome.save_fail_img()
        chrome.home()
        chrome.browser_webpage(website="hao123.com")
        if not chrome.save_bookmark(page=u"hao123导航-上网从这里开始"):
            chrome.logger.error("fail to add bookmark - hao123.com")
            chrome.save_fail_img()
        chrome.home()
        chrome.browser_webpage(website="mail.qq.com")
        if not chrome.save_bookmark(page=u"手机统一登录"):
            chrome.logger.error("fail to add bookmark - mail.qq.com")
            chrome.save_fail_img()
        chrome.home()
        chrome.browser_webpage(website="www.sohu.com")
        if not chrome.save_bookmark(page=u"手机搜狐网"):
            chrome.logger.error("fail to add bookmark - sohu.com")
            chrome.save_fail_img()
        chrome.home()
        chrome.device(resourceId="com.android.chrome:id/menu_button").click.wait(timeout=2000)
        chrome.device(text="Bookmarks").click.wait()
        if chrome.device(resourceId='com.android.chrome:id/bookmark_row').count >= 5:
            chrome.logger.debug("Add Bookmarks successful")
            return True
        chrome.logger.debug("Add Bookmarks FAIL!!!")
    except:
        chrome.logger.debug("Add Bookmarks FAIL!!!")
        chrome.logger.warning(traceback.format_exc())
        chrome.save_fail_img()
        return False


def dismiss_chrome_welcome(chrome):
    try:
        chrome.logger.debug("Enter Chrome to cancel permission page")
        if not chrome.start_app("Chrome"):
            chrome.logger.debug("fail to enter chrome")
            chrome.save_fail_img()
            return False
        if chrome.device(text="ACCEPT & CONTINUE").wait.exists(timeout=10000):
            chrome.device(text="ACCEPT & CONTINUE").click.wait()
        if chrome.device(text="Sign in to Chrome").wait.exists(timeout=2000):
            chrome.device(text="NO THANKS").click.wait()

        while chrome.device(text="KEEP GOOGLE").wait.exists():
            chrome.device(text="KEEP GOOGLE").click()

        if chrome.device(resourceId="com.android.chrome:id/menu_button").wait.exists(timeout=2000):
            return True
        chrome.logger.debug("fail to dismiss chrome welcome page")
        chrome.save_fail_img()
        return False
    except:
        chrome.logger.warning(traceback.format_exc())
        chrome.save_fail_img()
        return False


def dismiss_player_welcome(settings):
    settings.logger.debug("Enter Music Player to cancel permission page")
    if not settings.start_app("Play Music"):
        settings.logger.debug("fail to enter music player")
        settings.save_fail_img()
        return False
    if settings.device(text="Listen Now").wait.exists(timeout=30000):
        settings.logger.debug("Enter music player success")
        return True
    settings.logger.debug("Fail to dismiss welcome page of music player")
    settings.save_fail_img()


def dismiss_camera_welcome(settings):
    try:
        settings.logger.debug("Enter Camera to cancel permission page")
        if not settings.start_app("Camera"):
            settings.logger.debug("fail to enter camera")
            settings.save_fail_img()
            return False
        if settings.device(text="SKIP INTRO").wait.exists(timeout=8000):
            settings.device(text="SKIP INTRO").click.wait()
        if settings.device(text="SKIP").wait.exists(timeout=8000):
            settings.device(text="SKIP").click.wait()
        if settings.device(resourceId="com.blackberry.camera:id/overlay_btn").exists:
            settings.device(resourceId="com.blackberry.camera:id/overlay_btn").click.wait()
        settings.device(description="Flash Auto").click.wait()
        settings.device(description="Flash Off").click.wait()
        settings.device.wait("idle")
        settings.device(description="HDR Auto").click.wait()
        settings.device(description="HDR Off").click.wait()
        settings.device(resourceId="com.blackberry.camera:id/capture_button_icon").click.wait()
        return True
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()
        return False


def dismiss_calendar_welcome(settings):
    try:
        settings.logger.debug("Enter Calendar to cancel permission page")
        if not settings.start_app("Calendar"):
            return False
        if settings.device(text="SKIP INTRO").wait.exists(timeout=8000):
            settings.device(text="SKIP INTRO").click.wait()
        while settings.device(text="ALLOW").exists:
            settings.device(text="ALLOW").click.wait()
        settings.device.wait("idle")
        if not settings.device(description="Navigation Drawer Open").exists:
            settings.logger.error("enter calendar fail")
            settings.save_fail_img()
            return False
        return True
        # settings.device(description="Navigation Drawer Open").click.wait()
        # settings.device(description="Drop down tcllijunjun@gmail.com").click.wait()
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()
        return False


def import_contacts(settings, phone_num):
    if enter_contacts(settings):
        settings.device(description="More options").click.wait()
        settings.device(text="Import/export").click.wait()
        settings.device(text="Import from storage").click.wait()
        if settings.device(text="ALLOW").wait.exists():
            settings.device(text="ALLOW").click.wait()
        if settings.device(text="Local contacts").exists:
            settings.device(text="Local contacts").click.wait()
        if settings.device(text="Import contacts from vCard?").wait.exists():
            settings.device(text="OK").click.wait()
        settings.device(text="Import one vCard file").click.wait()
        settings.device(text="OK").click.wait()
        settings.device(textStartsWith=phone_num).click.wait()
        settings.device(text="OK").click.wait()
        settings.device.open.notification()
        settings.device.wait("idle")
        if settings.device(textStartsWith="Finished importing").wait.exists(timeout=20000):
            settings.logger.debug("import contacts successful")
            return True
    else:
        settings.logger.debug("enter_contacts fail")
    settings.logger.debug("import contacts fail")
    settings.save_fail_img()
    return False


def enter_contacts(settings):
    try:
        settings.logger.debug("Enter Contacts to cancel permission page")
        if settings.device(text="ALL CONTACTS").exists:
            settings.device(text="ALL CONTACTS").click.wait()
            return True
        if not settings.start_app("Contacts"):
            return False
        if settings.device(text="GRANT PERMISSIONS").wait.exists(timeout=3000):
            settings.device(text="GRANT PERMISSIONS").click.wait()
        index = 0
        while settings.device(text="ALLOW").wait.exists(timeout=3000) and index < 8:
            settings.device(text="ALLOW").click.wait()
            index += 1
        if settings.device(text="SKIP").wait.exists(timeout=5000):
            settings.device(text="SKIP").click.wait()
        if settings.device(description="Close navigation drawer").wait.exists(timeout=5000):
            settings.device(description="Close navigation drawer").click.wait()
        if settings.device(description="Open navigation drawer").wait.exists(timeout=2000):
            settings.device(text="ALL CONTACTS").click.wait()
            return True
        return False
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()
        return False


def disable_auto_update(settings):
    try:
        if not settings.start_app("Play Store"):
            settings.logger.debug("fail to enter Play Store")
            settings.save_fail_img()
            return False
        if not settings.device(resourceId="com.android.vending:id/navigation_button").wait.exists(timeout=30000):
            if settings.device(text="ACCEPT").exists:
                settings.device(text="ACCEPT").click.wait(timeout=5000)
            else:
                settings.logger.debug("fail to enter Play Store")
                settings.save_fail_img()
                return False
        settings.device(resourceId="com.android.vending:id/navigation_button").click.wait()
        settings.device(scrollable=True, resourceId="com.android.vending:id/play_drawer_list"). \
            scroll.vert.to(text="Settings")
        settings.device(text="Settings").click.wait()
        if not settings.device(text="Auto-update apps").wait.exists(timeout=5000):
            settings.logger.debug("fail to enter Play Store Settings")
            settings.save_fail_img()
            return False
        settings.device(text="Auto-update apps").click.wait()
        settings.device(text="Do not auto-update apps").click.wait()
        if settings.device(text="Do not auto-update apps").wait.exists(timeout=5000):
            settings.logger.debug("disable auto update successful")
            return False
        settings.logger.debug("disable auto update fail")
        settings.save_fail_img()
        return True
    except:
        settings.logger.warning(traceback.format_exc())
        settings.save_fail_img()


def add_google_account(settings):
    if not settings.enter_settings("Accounts"):
        settings.logger.debug("fail to enter Settings Accounts")
        return False
    settings.device(text="Add account").click.wait()
    settings.device(scrollable=True).scroll.vert.to(text="Google")
    settings.device(text="Google").click.wait()
    wait_time = 0
    max_wait_time = 3 * 60
    settings.logger.debug(max_wait_time)
    while not settings.device(description="Sign in").exists:
        if wait_time > max_wait_time:
            settings.logger.debug("enter google sign in page fail, check your network")
            settings.save_fail_img()
            settings.back_to_home()
            return False
        settings.logger.debug("sleep 3s")
        wait_time += 3
        time.sleep(3)
    settings.device(text="Email or phone").set_text("tcllijunjun")
    settings.device.wait("idle")
    settings.device(description="NEXT").click.wait()

    wait_time = 0
    while not settings.device(text="Enter your password").exists:
        if wait_time > max_wait_time:
            settings.logger.debug("enter google password page fail, check your network")
            settings.save_fail_img()
            settings.back_to_home()
            return False
        wait_time += 3
        time.sleep(3)
    settings.device(text="Enter your password").set_text("lijunjun210")
    settings.device.wait("idle")
    settings.device(description="NEXT").click.wait()

    if settings.device(description="By signing in, you agree to the ").wait.exists(timeout=20000):
        settings.device(description="I AGREE").click.wait()
    if settings.device(text="Google services").wait.exists(timeout=20000):
        settings.device(text="NEXT").click.wait()
    if settings.device(text="Add account").wait.exists(timeout=20000):
        settings.logger.debug("add google account successfully")
        return True
    settings.logger.debug("add google account fail")
    settings.save_fail_img()
    settings.back_to_home()
    return False


def setup_display(settings):
    if not settings.enter_settings("Display"):
        settings.logger.debug("fail to enter Display setting")
        settings.save_fail_img()
        settings.back_to_home()
        return False
    settings.device(text="Brightness level").click.wait()
    settings.device(text="Display brightness").click.topleft()
    settings.device.wait("idle")
    settings.back_to_home()
    settings.logger.debug("display setup successful")
    return True


def setup_sound(settings):
    settings.logger.debug("setup sound")
    if not settings.enter_settings("Sound"):
        settings.save_fail_img()
        settings.back_to_home()
        return False
    settings.device(resourceId="android:id/seekbar").click.topleft()
    settings.device.wait("idle")
    # settings.device(text="Silent mode", checked=False).click.topleft() #for Krypton
    # settings.device.wait("idle") #for Krypton
    settings.device(scrollable=True).scroll.vert.to(text="Other sounds")
    settings.device.wait("idle")
    settings.device(text="Other sounds").click.wait()
    for i in range(5):
        if settings.device(text="ON").exists:
            settings.device(text="ON").click.wait()
    settings.device.wait("idle")
    settings.back_to_home()
    return True


permission_list = ["SMS", "Calendar", "Camera", "Contacts", "Location", "Microphone", "Phone", "SMS", "Storage"]


def check_app_permission(settings):
    settings.logger.debug("setup app permission")
    if not settings.enter_settings("Apps"):
        settings.save_fail_img()
        settings.back_to_home()
        return False
    settings.device(resourceId="com.android.settings:id/advanced").click.wait()
    settings.device(text="App permissions").click.wait()
    if not settings.device(text="Body Sensors").exists:
        settings.save_fail_img()
        settings.back_to_home()
        return False
    for i in permission_list:
        settings.logger.debug("app permission - " + i)
        settings.device(scrollable=True).scroll.vert.to(text=i)
        settings.device(text=i).click.wait()
        while settings.device(text="OFF").exists or \
                (settings.device(scrollable=True).exists and settings.device(scrollable=True).scroll.vert.to(
                    text="OFF")):
            settings.device(text="OFF").click.wait()
        settings.device.press.back()
        settings.device.wait("idle")
    return True


if __name__ == "__main__":
    # print sys.argv[1]
    # device_id = sys.argv[1]
    # # device_id = "1163746968"
    # print "--------------------------    START!!!    ---------------------------------------------"
    # if "DEVICE" in device_id:
    #     device_id = os.environ.get(device_id)
    # # print "flash sw..."
    # # bat_path = os.path.split(os.path.realpath(__file__))[0] + "\\flashall.bat -d %s" % device_id
    # # os.system(bat_path)
    # wait_for_full_device_boot(None, device_id)
    # command = "adb -s %s shell settings put global verifier_verify_adb_installs 0" % device_id
    # os.system(command)
    # command = "adb -s %s shell svc power stayon true" % device_id
    # os.system(command)
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(PreSetUp)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
    print "--------------------------    FINISH!!!    ---------------------------------------------"
