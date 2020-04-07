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


class TestTelephony(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        serinoM = "MDEVICE"
        serinoS = "SDEVICE"
        # serinoM = "5000000100"
        # serinoS = "5900000036"
        cls.mod = Telephony(serinoM, "TelephonyLTE", serinoS)
        cls.set = Settings(cls.mod.device, "settings")
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(
            text="Close app")

    @classmethod
    def tearDownClass(cls):
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR").remove()
        cls.mod.clear_notification()
        cls.mod.logger.debug("Telephony Mission Complete")
        cls.mod.logger.info("Success Times: %s." % cls.mod.suc_times)
        rate = cls.mod.suc_times / cls.mod.test_times * 100
        if rate < 95:
            cls.mod.logger.warning("Result Fail Success Rate Is " + str(rate) + '%')
        else:
            cls.mod.logger.info("Result Pass Success Rate Is " + str(rate) + '%')
        # cls.mod.charging_full(critical=20)

    def setUp(self):
        self.mod.back_to_home()
        # self.mod.logger.info("battery capacity: %s" % self.mod.adb.shell("dumpsys battery"))
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def tearDown(self):
        self.mod.back_to_home()
        # self.mod.logger.info("battery capacity: %s" % self.mod.adb.shell("cat sys/class/power_supply/battery/capacity"))
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def test4CallLTE(self):
        """Test telephony from dialer, contact or call history in All(LTE/WCDMA/GSM) network
        """
        self.set.switch_network("ALL")
        # todo: switch VOLTE
        self.case_call("Dialer", int(self.mod.dicttesttimes.get("DialerLTE".lower())))
        self.case_call("Contact", int(self.mod.dicttesttimes.get("ContactLTE".lower())))
        self.case_call("History", int(self.mod.dicttesttimes.get("CallLogLTE".lower())))

    def case_call(self, call_type, times):
        """case function, m-device call s-device from Dialer、Contact、History
           check call and end call results
        """
        self.mod.logger.info("Call from %s %d times." % (call_type, times))
        self.mod.start_call_app(call_type)
        for loop in range(times):
            try:
                if self.mod.call(call_type, loop, mutil=True) and self.mod.end_call("mu"):
                    self.mod.suc_times += 1
                    self.mod.logger.info("Trace Success Loop %s." % (loop + 1))
                else:
                    self.mod.exception_end_call()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exception_end_call()
                self.mod.start_call_app(call_type)
            finally:
                self.mod.device.delay()
                self.mod.back_to_call_app(call_type)
        self.mod.back_to_home()
        self.mod.logger.info("Call from %s %d times completed" % (call_type, times))


if __name__ == "__main__":
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestTelephony)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
