#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

from TclTools.TATServer import send_mail

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not lib_path in sys.path:
    sys.path.append(lib_path)
from common import Common
from configs import GetConfigs
from ConfigParser import NoSectionError
import log_utils
import utils
from TclTools.MailHelper import MailHelper

class BaseTestCase(unittest.TestCase):
    test_mod = 'common'
    success_times = 0
    fail_times = 0
    total_times = 0

    @classmethod
    def setUpClass(cls):
        serino = utils.get_m_device()
        # f2cd923a 4bb3fe65 9929f085
        # serino = 'GAWKFQT8WGL7L7S8'
        cls.logger = log_utils.createlogger(cls.test_mod)
        cls.trace_total()
        cls.c = Common(serino, cls.test_mod)
        cls.c.device.watcher('AUTO_FC_WHEN_ANR') \
            .when(textContains='isn\'t responding') \
            .when(text='Close app') \
            .click(text='Close app')

        cls.c.device.watcher('ALLOW')\
            .when(text='ALLOW')\
            .when(resourceId="com.android.packageinstaller:id/permission_allow_button")\
            .click(text='ALLOW')

        cls.c.device.watcher('OPTI_CANCEL')\
            .when(text='App optimization')\
            .when(text='CANCEL')\
            .click(text='CANCEL')

        # WD, open app downloaded from playstore first time, 'Autostart' menu popup, click cancel.
        cls.c.device.watcher('Autostart').when(text='Autostart').when(text='CANCEL').click(text='CANCEL')

    @classmethod
    def tearDownClass(cls):
        cls.logger.info('{} Mission Complete'.format(cls.test_mod))
        cls.trace_pass_rate()
        cls.c.device.watchers.remove()
        cls.c.clear_notification()
        cls.trace_pass_rate()
        cls.c.charging_full2()

    def setUp(self):
        self.c.back_to_home()
        self.c.battery_status()
        # self.c.generate_bugreport()
        self.send_mail_if_fullramdump_generated()

    def send_mail_if_fullramdump_generated(self):
        ret = self.c.adb.check_fullramdump()
        print 'check full ramdump', ret
        if ret is None:
            return
        else:
            print 'check full ramdump :{}'.format(ret)
            if self.check_ramdump_exists(ret):
                return
        self.do_send_mail(ret)

        remote_path = 'sdcard/{}'.format(ret)
        out = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        self.c.adb.cmd('pull', remote_path, out)

    def do_send_mail(self, ret):
        serrial = self.c.adb.device_serial()
        subject = '[{}]Found fullramdump'.format(serrial)

        response = send_mail(ret, serrial, subject)
        if response is not True:
            self.logger.error(response)
            mail = MailHelper()
            mail.send_customized_mail('[{}]Found fullramdump wd'.format(serrial), ret, 'di.wu@tcl.com')

    def check_ramdump_exists(self, line):
        file_path = r'D:\fullramdump_list.txt'
        found = False
        with open(file_path, 'a+') as f:
            lines = f.readlines()
            if line in lines:
                print "{} already report.".format(line)
                found = True
            else:
                f.write('{}\n'.format(line))
        return found


    def tearDown(self):
        self.c.back_to_home()
        self.c.battery_status()

    @classmethod
    def trace_success(cls):
        cls.success_times += 1
        cls.logger.info('Trace Success Loop {}.'.format(cls.success_times))

    @classmethod
    def trace_fail(cls):
        cls.fail_times += 1
        cls.logger.info('Trace Fail Loop {}.'.format(cls.fail_times))

    @classmethod
    def trace_total(cls):
        try:
            cls.mod_cfg = GetConfigs(cls.test_mod)
            cls.dicttesttimes = cls.mod_cfg.get_test_times()
            for test_time in cls.dicttesttimes:
                cls.total_times += int(cls.dicttesttimes[test_time])
            cls.logger.info('Trace Total Times {}'.format(cls.total_times))
        except NoSectionError:
            print(traceback.format_exc())

    @classmethod
    def trace_pass_rate(cls):
        cls.logger.info('Success Times: {}.'.format(cls.success_times))
        rate = cls.success_times / cls.total_times * 100
        if rate < 95:
            cls.logger.warning('Result Fail Success Rate Is {}%'.format(rate))
        else:
            cls.logger.info('Result Pass Success Rate Is {}%'.format(rate))
