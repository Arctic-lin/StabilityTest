#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import random
import sys
import traceback
import unittest



lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.gmail import Gmail
from common.settings import Settings, Wifi
from common.base_test_case import BaseTestCase
from common.mods import Mods

class TestGmail(BaseTestCase):
    test_mod = Mods.Gmail

    @classmethod
    def setUpClass(cls):
        """必须开启翻墙wifi"""
        super(TestGmail, cls).setUpClass()
        cls.mod = Gmail(cls.c.device, cls.test_mod)
        cls.set = Settings(cls.mod.device, "Settings")
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")
        cls.mod.device.watcher("GMAIL_DISMISS").when(description="Dismiss tip").click(text="Dismiss tip")
        cls.mod.clear_background()
        # cls.mod.disable_wifi()
        cls.wifi = Wifi(cls.mod.device, "task_Wifi")
        cls.wifi.connect_wifi(cls.mod.config.getstr("wifi_name", "Wifi", "common"),
                              cls.mod.config.getstr("wifi_password", "Wifi", "common"),
                              cls.mod.config.getstr("wifi_security", "Wifi", "common"))



    def setUp(self):
        super(TestGmail, self).setUp()
        self.receiver = random.choice(self.mod.config.getstr("Email_receiver", "Email", "common").split(","))

    def test_gmail_with_4G(self):
        # gamil must be test on wifi
        # self.set.switch_network_for_multi_menus("ALL")

        self.case_forward(receiver=self.receiver, with_attechment=True, times=int(self.dicttesttimes.get("Fwd1LTE".lower())))
        self.case_forward(receiver=self.receiver, with_attechment=False, times=int(self.dicttesttimes.get("Fwd0LTE".lower())))

    def case_forward(self,receiver,  with_attechment, times=1):
        """case function, forward email
        """
        self.mod.logger.info("forward email test with attachment=%s %d times" % (with_attechment, times))
        self.mod.enter()
        for loop in range(times):
            try:
                self.mod.enter()
                if self.mod.create_mail_and_sent(receiver, with_attechment):
                    self.trace_success()
                else:
                    self.trace_fail()

            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.device.delay()
                self.mod.back_to_home()

        # self.mod.del_all_sent()
        # self.mod.empty_trash()
        self.mod.back_to_home()
        self.mod.logger.info("forward email test with attachment=%s %d times completed" % (with_attechment, times))

    def case_draft(self, receiver, times=1):
        """case function, forward email
        """
        self.mod.logger.info("draft email test %d times" % times)
        self.mod.enter()
        for loop in range(times):
            try:
                self.mod.enter()
                if self.mod.save_draft_and_sent(receiver) and self.mod.del_all_sent():
                    self.trace_success()
                else:
                    self.trace_fail()

            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exception_end_call()

            finally:
                self.mod.device.delay()
                self.mod.back_to_home()
        self.mod.back_to_home()
        self.mod.logger.info("draft email test %d times completed" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestGmail)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
