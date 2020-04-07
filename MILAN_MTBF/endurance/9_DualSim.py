# -*- coding: utf-8 -*-
from __future__ import division

import os
import random
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not lib_path in sys.path:
    sys.path.append(lib_path)
from common.settings import DualSim
from common.telephony import Telephony
from common.message import Message
from common.base_test_case import BaseTestCase
from common.mods import Mods

class DualSimEndurance(BaseTestCase):
    test_mod = Mods.Dualsim
    @classmethod
    def setUpClass(cls):
        super(DualSimEndurance, cls).setUpClass()
        cls.mod = DualSim(cls.c.device, cls.test_mod)
        cls.tel = Telephony(cls.c.device, "sim_telephony")
        cls.msg = Message(cls.c.device, "sim_message")
        cls.carrier_service_num = cls.mod.get_carrier_service_num()

    @classmethod
    def tearDownClass(cls):
        super(DualSimEndurance, cls).tearDownClass()

    # @unittest.skip("debug")
    def test_call(self):
        """
        ENDURANCE_DUALSIM_CS_001                双卡拨号键盘拨打电话          100
        ENDURANCE_DUALSIM_CS_002                双卡电话簿中拨打电话          100
        ENDURANCE_DUALSIM_CS_003                双卡call log中拨打电话        100
        :return:
        """
        for i in range(1, 2):
            self.mod.back_to_home()
            self.mod.select_preferred_sim(sim=i, action="call")
            self.mod.back_to_home()
            # self.case_call("Dialer", int(self.dicttesttimes.get("call_from_dialer_times".lower())))
            self.case_call("Contact", int(self.dicttesttimes.get("call_contact_times".lower())))
            self.case_call("History", int(self.dicttesttimes.get("call_callLog_times".lower())))

    # @unittest.skip("debug")
    def test_msg(self):
        """
        ENDURANCE_DUALSIM_CS_004                双卡发送短信                  30
        :return:
        """
        self.case_forward_msg(int(self.dicttesttimes.get("fwd_msg_times".lower())), sim=1)
        self.case_forward_msg(int(self.dicttesttimes.get("fwd_msg_times".lower())), sim=2)

    # @unittest.skip("debug")
    def test_switch(self):
        """
        ENDURANCE_DUALSIM_SWITCHNETWORK_001     双卡网络模式切换 SIM1       100
        ENDURANCE_DUALSIM_SWITCHNETWORK_002     双卡网络模式切换  SIM2      100
        :return:
        """
        self.case_switch_sim(1, int(self.dicttesttimes.get("swipe_sim1_set".lower())))
        self.case_switch_sim(2, int(self.dicttesttimes.get("swipe_sim2_set".lower())))

    # @unittest.skip("debug")
    def test_switch_data(self):
        """
        ENDURANCE_DUALSIM_PS_001                双卡SIM1数据业务启用/关闭     100
        ENDURANCE_DUALSIM_PS_002                双卡SIM2数据业务启用/关闭     100
        ENDURANCE_DUALSIM_PS_003                双卡SIM1/SIM2数据业务切换	     100  removed
        :return:
        """
        self.case_switch_data(1, int(self.dicttesttimes.get("swipe_sim1_data_set".lower())))
        self.case_switch_data(2, int(self.dicttesttimes.get("swipe_sim2_data_set".lower())))

    def case_switch_sim(self, sim_card, times):
        self.mod.logger.info("switch sim card %d %d times" % (sim_card, times))
        try:
            self.mod.select_preferred_sim(sim=sim_card, action="data")
            self.mod.device.press.home()
            self.mod.enter_sim()
            self.mod.switch_sim_new(sim_card)
        except:
            self.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()

        for loop in range(times):
            try:
                if self.mod.select_preferred_net_type("3G", sim_card) and self.mod.select_preferred_net_type("LTE",
                                                                                                             sim_card):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.select_preferred_sim(sim=1, action="data")
        self.mod.logger.info("switch sim card %d %d times completed" % (sim_card, times))

    def case_switch_data(self, sim_card, times):
        self.mod.logger.info("switch sim card %d data %d times" % (sim_card, times))
        self.mod.select_preferred_sim(sim_card, action="data")
        self.mod.device.press.home()
        self.mod.enter_data()
        for loop in range(times):
            try:
                if self.mod.switch_data_new(sim_card, "OFF") and self.mod.switch_data_new(sim_card, "ON"):
                    # if self.mod.switch_data(sim_card, "OFF") and self.mod.switch_data(sim_card, "ON"):
                    self.trace_success()
            except:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.select_preferred_sim(sim=1, action="data")
        self.mod.logger.info("switch sim card %d data %d times completed" % (sim_card, times))

    def case_call(self, call_type, times):
        """call_type(Dialer、Contact、History)
        """
        self.mod.logger.info("sim1 and sim2 Call from %s %d times." % (call_type, times))
        for loop in range(times):
            try:
                if self.tel.call_10010(call_type, loop, 1, open_app=True) and self.tel.end_call(device="mu") \
                        and self.tel.call_10010(call_type, loop, 2, open_app=True) and self.tel.end_call(device="mu"):
                    self.trace_success()
                else:
                    self.mod.exception_end_call()
            except Exception, e:
                self.mod.logger.error(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.exception_end_call()
            finally:
                self.mod.back_to_home()
        self.mod.logger.info("sim1 and sim2 Call from %s %d times completed" % (call_type, times))

    def case_forward_msg(self, times, sim=1):
        """case function, forward message case.
        arg: msg_type(str) -- sms or mms.
        """
        self.mod.logger.debug("sim1 and sim2 Send message %s times." % times)
        self.mod.select_preferred_sim(sim, action="msg")
        self.mod.device.press.home()
        for loop in range(times):
            try:
                self.msg.enter_new()
                msg_type = random.choice(["SMS", "MMS"])
                if self.msg.fwd_msg(msg_type, "10010") and self.msg.back_to_message():
                    self.trace_success()
                self.msg.delete_extra_msg()
            except Exception, e:
                self.mod.logger.error(e)
                self.mod.save_fail_img()
            finally:
                self.mod.back_to_home()
        self.mod.select_preferred_sim(sim=1, action="msg")
        self.mod.logger.debug("sim1 and sim2 Send message %s times." % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(DualSimEndurance)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
