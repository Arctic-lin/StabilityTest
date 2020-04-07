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
from common.schedule import Schedule
from common.mods import Mods
from common.base_test_case import BaseTestCase

class TestPim(BaseTestCase):
    test_mod = Mods.Pim

    @classmethod
    def setUpClass(cls):
        """wifi 开启与否不影响测试"""
        super(TestPim, cls).setUpClass()
        cls.mod = Schedule(cls.c.device, cls.test_mod)
        cls.mod.device.watcher("AUTO_FC_WHEN_ANR")\
            .when(textContains="isn't responding")\
            .when(text="Close app")\
            .click(text="Close app")

    def test_pim(self):
        try:
            self.case_add_del_calendars(int(self.dicttesttimes.get("Calendar".lower())))
            self.case_add_del_alarms(int(self.dicttesttimes.get("Alarms".lower())))
            self.case_add_del_wclock(int(self.dicttesttimes.get("Wclock".lower())))
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()

    def case_add_del_calendars(self, times):
        self.mod.logger.debug('Add and delete a Calendar ' + str(times) + ' Times')
        self.mod.enter_calendar()
        # self.mod.delete_calendar_all()
        for loop in range(times):
            try:
                name = self.mod.random_name(loop) + "_" + self.mod.adb.get_device_seriono()[-4:]
                if self.mod.create_calendar(name) and self.mod.delete_calendar(name):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.enter_calendar()
        self.mod.back_to_home()
        self.mod.logger.debug('Add and delete a Calendar Test complete')

    def case_add_del_alarms(self, times=1):
        self.mod.logger.debug('Add and delete an alarm ' + str(times) + ' Times')
        self.mod.enter_alarm()
        self.mod.delete_alarm_tct()
        for loop in range(times):
            try:
                if self.mod.add_alarm_tct() and self.mod.delete_alarm_tct():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.delete_alarm()
        self.mod.back_to_home()
        self.mod.logger.debug('Add and delete an alarm Test complete')

    def case_add_del_wclock(self, times=1):
        self.mod.logger.debug('Add and delete two world clocks ' + str(times) + ' Times')
        cities = ['Abidjan', 'Accra', 'Amman', 'Anadyr']
        city2 = random.sample(cities, 2)
        for loop in range(times):
            try:
                self.mod.enter_wclock()
                if self.mod.add_wclock_tct(city2) and self.mod.delete_wclock_tct(city2):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.back_to_home()
        self.mod.logger.debug('Add and delete World clocks Test complete')


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestPim)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)
