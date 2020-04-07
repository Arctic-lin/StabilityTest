# -*- coding: utf-8 -*-
# Precondition: Set Sdevice name as S-DEVICE
from __future__ import division

import os
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lib_path not in sys.path:
    sys.path.append(lib_path)

from common.telephony import Telephony


class MusicInterrupt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mdevice = "MDEVICE"
        sdevice = "SDEVICE"
        # mdevice = "5000002595"
        # sdevice = "5000002965"
        cls.mod = Telephony(mdevice, "Telephony", sdevice)

    @classmethod
    def tearDownClass(cls):
        cls.mod.logger.debug('Music interrupt Mission Complete')
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

    def testMusicInterrupt(self):
        """
        ENDURANCE_MUSIC_INTERRUPT_001   音乐播放中接听电话   20
        """
        self.case_interaction_with_sdevice(int(self.mod.dicttesttimes.get("music_interrupt".lower())))

    def case_interaction_with_sdevice(self, times=1):
        """do interaction when calling s_device
        """
        self.mod.logger.info("Do interaction %d times when calling sdevice." % times)

        try:
            if self._wrapped_play_music():
                for loop in range(times):
                    if self.mod.answer_musicing() and self._end_call_and_verify():
                        self.mod.suc_times += 1
                        self.mod.logger.info("Trace Success Loop " + str(loop + 1))
                    else:
                        self.mod.exception_end_call()
            else:
                self.mod.logger.error("Play music failed")
        except:
            self.mod.logger.warning(traceback.format_exc())
            self.mod.save_fail_img()
            self.mod.exception_end_call()

        self.mod.logger.info("Do interaction %d times when calling sdevice success." % times)

    def _wrapped_play_music(self):
        self.mod.logger.info("start music")
        self.mod.music.enter()
        return self.mod.music.play_music()

    def _end_call_and_verify(self):
        self.mod.end_call(device="mu")
        return self.mod.music.is_music_home()


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(MusicInterrupt)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
