# -*- coding: utf-8 -*-
# Precondition: Set Sdevice name as S-DEVICE
from __future__ import division

import os
import sys
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)
from common.settings import Bt


class BtSwitchEndurance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ##自适配是TAT正式测试 和 Pycharm debug 测试。省去频繁注释serino代码的操作。add by zw
        is_tat_test = os.environ.get("MDEVICE")
        cls.sdevice_id = ""
        if is_tat_test:
            mdevice = "MDEVICE"
            sdevice = "SDEVICE"
            cls.sdevice_id = os.environ.get("SDEVICE")
        else:
            mdevice = "5000002595"
            sdevice = "5000002965"
            cls.sdevice_id = "5000002965"

        cls.mod = Bt(mdevice, "Btswitch")
        cls.s_mod = Bt(sdevice, "S_Btswitch")
        cls.mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        cls.s_mod.device.watcher("WIFI_ENCRYPTION").when(text="REMAIN CONNECTED").click(text="REMAIN CONNECTED")
        # cls.mod.device.watcher("AUTO_FC_WHEN_ANR").when(textContains="isn't responding").when(text="Close app").click(text="Close app")

    @classmethod
    def tearDownClass(cls):
        # cls.mod.device.watcher("AUTO_FC_WHEN_ANR").remove()
        cls.mod.device.watcher("WIFI_ENCRYPTION").remove()
        cls.s_mod.device.watcher("WIFI_ENCRYPTION").remove()
        cls.mod.logger.debug('BT Mission Complete')
        cls.mod.logger.info("Success Times: %s." % cls.mod.suc_times)
        rate = cls.mod.suc_times / cls.mod.test_times * 100
        if rate < 95:
            cls.mod.logger.warning("Result Fail Success Rate Is " + str(rate) + '%')
        else:
            cls.mod.logger.info("Result Pass Success Rate Is " + str(rate) + '%')

    def setUp(self):
        self.mod.back_to_home()
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def tearDown(self):
        self.mod.back_to_home()
        self.mod.logger.info("battery status: %s" % self.mod.adb.shell("dumpsys battery"))

    def testEndurance(self):
        """
        ENDURANCE_BT_PAIR_001   BT配对    200
        transfer case removed from version: V1.2_Trail Run
        set Sdevice = S-DEVICE
        """
        self.case_compare(int(self.mod.dicttesttimes.get("bt_compare_times".lower())))
        # self.case_transfer(int(self.mod.dicttesttimes.get("bt_transfer_times".lower())))

    def case_transfer(self, times):
        self.mod.logger.info("m-device transfer file to s-device %d times" % times)
        self.mod.enter_s()
        self.mod.switch_s("ON")
        self.mod.enter()
        self.mod.switch("ON")
        self.mod.compare()
        for loop in range(times):
            try:
                if self.mod.transfer("02 - Madness.mp3"):
                    self.mod.suc_times += 1
                    self.mod.logger.info("Trace Success Loop %s." % (loop + 1))
            except Exception, e:
                self.mod.logger.warning(e)
                self.mod.save_fail_img()
        self.mod.enter()
        self.mod.cancel_compare()
        self.mod.switch("OFF")
        self.mod.switch_s("OFF")
        self.mod.back_to_home()
        self.mod.back_to_home_s()
        self.mod.logger.info("m-device transfer file to s-device %d times completed" % times)

    def case_compare(self, times=1):
        self.mod.logger.info("m-device compare s-device %d" % times)
        self.s_mod.enter_bt()
        self.s_mod.switch("ON")
        self.s_mod.rename_bt_sdevice(self.sdevice_id)
        self.mod.enter_bt()
        self.mod.switch("ON")
        for loop in range(times):
            try:
                if self.mod.compare(self.sdevice_id):
                    self.s_mod.device(text="PAIR").wait.exists(timeout=5000)
                    self.s_mod.device(text="PAIR").click()
                    self.mod.device(text="PAIR").click()
                    if self.mod.device(resourceId="com.android.settings:id/settings_button").wait.exists(timeout=10000):
                        self.mod.logger.info("m-device compare s-device success")
                    else:
                        self.mod.logger.info("m-device compare s-device failed")
                        self.mod.save_fail_img()
                        continue
                else:
                    self.mod.logger.info("s-device bluetooth not exists")
                    self.mod.save_fail_img()
                if self.mod.cancel_compare() and self.s_mod.cancel_compare():
                    self.mod.suc_times += 1
                    self.mod.logger.info("Trace Success Loop %s." % (loop + 1))
                    self.mod.device.delay(5)
            except Exception, e:
                self.mod.logger.warning(e)
                self.mod.save_fail_img()
        self.s_mod.switch("OFF")
        self.s_mod.device.press.back()
        self.s_mod.device.press.home()
        self.mod.switch("OFF")
        self.mod.back_to_home()
        self.mod.logger.info("m-device compare s-device %d completed" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(BtSwitchEndurance)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
