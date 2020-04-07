#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import sys
import traceback
import unittest

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LIB_PATH not in sys.path:
    sys.path.append(LIB_PATH)
from common.tasking import MultiTask
from common.telephony import Telephony
from common.settings import Wifi
from common.mods import Mods
from common.base_test_case import BaseTestCase


class TestMultiTask(BaseTestCase):
    test_mod = Mods.Tasking

    @classmethod
    def setUpClass(cls):
        """需要开启wifi"""
        super(TestMultiTask, cls).setUpClass()
        mdevice = "MDEVICE"
        sdevice = "SDEVICE"
        # mdevice = "GAWKFQT8WGL7L7S8"
        # sdevice = "3dd7a889"

        cls.mod = MultiTask(mdevice, cls.test_mod, sdevice=sdevice)
        cls.tel = Telephony(mdevice, "task_tel", sdevice=sdevice)
        cls.wifi = Wifi(cls.mod.device, "task_Wifi")
        cls.mod.back_to_home()
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        cls.is_multi = True if cls.mod.config.site == "US" else False
        cls.s_tel = cls.mod.sdevice_tel if cls.is_multi else cls.mod.get_carrier_service_num()
        cls.mod.start()

    def testStability(self):
        self.case_interaction_with_carrier_service_num(int(self.dicttesttimes.get('ITERATION10010'.lower())))

    def case_interaction_with_carrier_service_num(self, times=1):
        """do interaction when calling 10010
        """
        self.mod.logger.info("Do interaction %d times when calling carrier service number." % times)
        for loop in range(times):
            try:
                if self.tel.call_smart("Dialer", open_app=True, multi=self.is_multi, s_tel=self.s_tel) and \
                        self.mod.interaction(
                            int(self.mod.appconfig("CALLSDEVICE", "Tasking"))) and self.tel.end_call_tasking(
                    self.is_multi):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.exception_end_call()
        self.mod.logger.info("Do interaction %d times when calling 10010 success." % times)

    def case_interaction_with_sdevice(self, times=1):
        """do interaction when calling s_device
        """
        self.mod.logger.info("Do interaction %d times when calling sdevice." % times)
        for loop in range(times):
            try:
                if self.tel.call("Dialer", open_app=True, mutil=True) and \
                        self.mod.interaction(int(self.mod.appconfig("CALLSDEVICE", "Tasking"))) and \
                        self.mod.adb.close_call_service():
                    self.trace_success()
                else:
                    self.trace_fail()
                    self.mod.exception_end_call()
            except:
                self.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exception_end_call()
        self.mod.logger.info("Do interaction %d times when calling sdevice success." % times)


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestMultiTask)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
