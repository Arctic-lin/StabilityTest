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
from common.mods import Mods
from common.message import Message
from common.settings import Settings
from common.base_test_case import BaseTestCase


class TestMessage(BaseTestCase):
    test_mod = Mods.Message

    @classmethod
    def setUpClass(cls):
        """wifi 开启与否不影响测试"""
        super(TestMessage, cls).setUpClass()
        mdevice = "MDEVICE"
        sdevice = "SDEVICE"
        # mdevice = "GAWKFQT8WGL7L7S8"
        # sdevice = "3dd7a889"
        cls.mod = Message(mdevice, cls.test_mod, sdevice)
        cls.set = Settings(cls.mod.device, "Settings")
        cls.is_multi = True if cls.mod.config.site == "US" else False

    # @unittest.skip("debug")
    def testStability3G(self):
        """
        send draft case is invalid, new message will not save as draft.
        :return:
        """
        if self.set.get_carrier_service_num() == "10086":
            self.set.logger.info("you are using CMCC sim card, using 4G instead of 3G test cases")
            self.set.switch_network_for_multi_menus("ALL")
        else:
            self.set.switch_network_for_multi_menus("3G")
        self.case_forward_msg('SMS', int(self.dicttesttimes.get("SMS3G".lower(), 0)))

    # @unittest.skip("debug")
    def testStabilityLTE(self):
        """
        send draft case is invalid, new message will not save as draft.
        :return:
        """
        self.set.switch_network_for_multi_menus("ALL")
        self.case_forward_msg('SMS', int(self.dicttesttimes.get("SMSLTE".lower(), 0)))
        self.case_forward_msg('MMS', int(self.dicttesttimes.get("MMSLTE".lower(), 0)))

    def case_forward_msg(self, msg_type, times=1):
        """case function, forward message case.
        arg: msg_type(str) -- sms or mms.
        check forward msg results
        """
        msg_receiver = self.mod.sdevice_tel if self.is_multi else self.mod.get_carrier_service_num()
        self.mod.logger.debug("Send %s %s times." % (msg_type, times))
        self.mod.enter_new()
        for loop in range(times):
            try:
                if self.mod.fwd_msg(msg_type, msg_receiver):
                    self.trace_success()
                else:
                    self.trace_fail()
                self.mod.delete_extra_msg()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.device.delay()
                self.mod.back_to_message()
        self.mod.back_to_home()
        self.mod.logger.debug("Send %s Msg Test complete." % msg_type)

    def quickReplyMsg(self, times):
        """case function, answer s-device message during play music
           check  receive、answer message and back to music results
        """
        self.mod.logger.debug("Quick reply during music %d times." % times)
        self.mod.music.play_music()
        for loop in range(times):
            try:
                if self.mod.s_send_msg(loop) and self.mod.answer_musicing(loop):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
        self.mod.back_to_home()
        self.mod.back_to_home_s()
        self.mod.music.close_music()
        self.mod.logger.debug("Quick reply during music %d times completed." % times)


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestMessage)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
