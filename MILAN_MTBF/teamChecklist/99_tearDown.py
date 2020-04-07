#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: 99_tearDown.py
@time: 2017/9/7 9:00

information about this file
"""

from __future__ import division

import os
import sys
import unittest

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)

from common.settings import Settings

from TclTools.MailHelper import MailHelper


class TestTearDown(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        is_tat_test = os.environ.get("MDEVICE")
        if is_tat_test:
            serino_m = "MDEVICE"
            cls.mdevice_id = os.environ.get(serino_m)
        else:
            serino_m = sys.argv[1]
            cls.mdevice_id = serino_m

        cls.mod = Settings(serino_m, "settings")

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_send_report(self):
        """
        read from log_path//test_result.txt
        generate report and send to team
        :return:
        """
        mail = MailHelper()
        pj = sys.argv[2]
        to_addr = sys.argv[3]

        body = sys.argv[4]
        subject = '[%s][%s]Team checklist finished' % (pj, self.mod.adb.get_device_version())
        mail.send_customized_mail(subject=subject, html_report=body, to_addrs=to_addr)


if __name__ == "__main__":
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestTearDown)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
