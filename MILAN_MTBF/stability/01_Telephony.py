#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)
from common.telephony import Telephony
from common.settings import Settings
from common.mods import Mods
from common.base_test_case import BaseTestCase
import random

class TestTelephony(BaseTestCase):
    test_mod = Mods.Telephony
    @classmethod
    def setUpClass(cls):
        """wifi 开启与否不影响测试"""
        super(TestTelephony, cls).setUpClass()
        mdevice = "MDEVICE"
        sdevice = "SDEVICE"
        # mdevice = "GAWKFQT8WGL7L7S8"
        # sdevice = "3dd7a889"
        cls.mod = Telephony(mdevice, cls.test_mod, sdevice)
        cls.set = Settings(mdevice, "settings")
        cls.carrier_service_num = cls.mod.get_carrier_service_num()
        cls.is_multi = True if cls.mod.config.site == "US" else False
        cls.s_tel = cls.mod.sdevice_tel if cls.is_multi else cls.mod.get_carrier_service_num()

    @classmethod
    def tearDownClass(cls):
        super(TestTelephony, cls).tearDownClass()
        cls.mod.clear_background()

    # @unittest.skip("debug")
    def test_01_Contacts(self):
        """Add and delete a contact in Phone or SIM
        """
        self.case_add_del_contact("Phone", int(self.dicttesttimes.get("ContactPhone".lower())))
    # @unittest.skip("debug")
    def test_02_Call3G(self):
        """Test telephony from dialer, contact or call history in 3g/2g network
        """
        if self.mod.config.testtype == "STABILITY":
            if self.carrier_service_num == "10086":
                self.set.logger.info("you are using CMCC sim card, using 4G instead of 3G test cases")
                self.set.switch_network_for_multi_menus("ALL")
            else:
                self.set.switch_network_for_multi_menus("3G")
        self.case_call("Dialer", int(self.dicttesttimes.get("Dialer3G".lower())))
        self.case_call("Contact", int(self.dicttesttimes.get("Contact3G".lower())))
        self.case_call("History", int(self.dicttesttimes.get("CallLog3G".lower())))

    # @unittest.skip("debug")
    def test_03_CallLTE(self):
        """Test telephony from dialer, contact or call history in All(LTE/WCDMA/GSM) network
        """

        if self.mod.config.testtype == "STABILITY":
            self.set.switch_network_for_multi_menus("ALL")
        self.case_call("Dialer", int(self.dicttesttimes.get("DialerLTE".lower())))
        self.case_call("Contact", int(self.dicttesttimes.get("ContactLTE".lower())))
        self.case_call("History", int(self.dicttesttimes.get("CallLogLTE".lower())))

    def case_call(self, call_type, times):
        """case function, m-device call s-device from Dialer、Contact、History
           check call and end call results
        """
        self.mod.logger.info("Call from %s %d times." % (call_type, times))
        self.mod.start_call_app(call_type)
        for loop in range(times):
            try:
                if self.mod.call_smart(call_type, loop, multi=self.is_multi, s_tel=self.s_tel) and self.mod.end_call(
                        "m"):
                    self.trace_success()
                else:
                    self.trace_fail()
                    self.mod.exception_end_call()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exception_end_call()
                self.mod.start_call_app(call_type)
            finally:
                self.mod.back_to_call_app(call_type)
        self.mod.back_to_home()
        self.mod.logger.info("Call from %s %d times completed" % (call_type, times))

    def delay_cucc(self):
        """
        add some delay in case the sim kill by CUCC
        :return:
        """
        wait_CUCC = random.randint(60, 120)
        self.mod.device.delay(wait_CUCC)

    def case_add_del_contact(self, path, times=1):
        """case function, add and delete contact form Phone or SIM
           check add、delete contact results
        """
        self.mod.logger.info('add delete contacts for {} {} times'.format(path, times))
        self.mod.enter_contacts()

        for loop in range(times):
            try:
                name = self.mod.random_name(loop)
                if self.mod.add_contact(path, name, self.s_tel) and self.mod.delete_contact(name):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.device.delay()
                self.mod.enter_contacts()
        self.mod.logger.info('add delete contacts for {} {} times completed'.format(path, times))


if __name__ == "__main__":
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestTelephony)
    suite = unittest.TestSuite([suiteCase])
    # print "bbbb",suite
    unittest.TextTestRunner(verbosity=2).run(suite)
