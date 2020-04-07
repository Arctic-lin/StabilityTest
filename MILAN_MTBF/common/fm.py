# -*- coding: UTF-8 -*-
__author__ = '93760'
"""Camera library for scripts.
"""

from common import Common


class FM(Common):

    def enter(self):
        """Launch music by StartActivity.
        """
        self.logger.debug('enter fm')
        if self.is_fm_home():
            return True

        self.start_app("Radio", b_desk=False)
        if self.device(text="Let app always run in background?").wait.exists(timeout=2000):
            self.device(text="ALLOW").click()
        if self.device(text="Insert headphone").wait.exists(timeout=3000):
            self.device(text="CONTINUE").click()

        if self.is_fm_home():
            return True
        else:
            self.logger.warning('enter fm fail!')
            return False
    def is_fm_home(self):
        if self.device(resourceId="com.tcl.fmradio:id/menu_audio_mode").wait.exists(timeout=5000):
            return True
        return False

    def exit(self):
        self.logger.info("exit radio")
        self.device.delay(2)
        if self.device(description="More options").exists:
            self.device(description="More options").click()
            self.device.delay(2)
            self.device(text="Exit").click()
        else:
            self.back_to_home()

    def switch(self, status="Stop"):
        """Play  Stop
        """
        self.logger.info("switch FM to %s" % status)
        now = "Stop" if status == "Play" else "Play"
        self.device.delay()
        if self.device(description=status).ext5:
            self.logger.info("FM status is already %s" % now)
            return True
        else:
            self.device(description=now).click()
            self.device.delay(5)
            if self.device(description=status).wait.exists(timeout=5000):
                self.logger.info("switch FM to %s success" % status)
                return True
            else:
                self.logger.info("switch FM to %s failed" % status)
                self.save_fail_img()
                return True

    def scan_channel(self):
        self.logger.info("scan channel")
        self.device.delay()

        # search channels
        self.device(resourceId="com.tcl.fmradio:id/menu_auto_search").click()

        # verify
        if self.device(text="CANCEL").wait.gone(timeout=120*1000):
            self.logger.info("scan channel success")
            return True
        else:
            self.logger.info("scan channel failed")
            self.save_fail_img()
            self.device(text="CANCEL").click()
            self.exit()
            return False

    def switch_channel(self):
        self.logger.info("switch channel during play radio")
        self.enter()
        self.switch("Play")
        if self.scan_channel():
            self.logger.info("switch channel 5 times")
            for i in range(5):
                self.device.delay(2)
                before_channel = self.device(resourceId="com.tct.fmradio.bb:id/channel_num").get_text()
                self.device(description="Go to next").click()
                self.device.delay(2)
                after_channel = self.device(resourceId="com.tct.fmradio.bb:id/channel_num").get_text()
                if after_channel != before_channel:
                    self.logger.info("switch channel %dth success" % (i + 1))
                else:
                    self.logger.info("switch channel %dth failed" % (i + 1))
                    self.save_fail_img()
                    self.exit()
                    return False
            self.logger.info("switch channel 5 times success")
            self.exit()
            return True
        else:
            return False

    def play_fm(self):
        print "self.config.testtype:", self.config.testtype
        fm_play_time = 60 if self.config.testtype.lower() == "endurance_mini" else 60 * 45
        self.logger.info("play radio %s seconds" % fm_play_time)
        self.enter()
        self.scan_channel()
        self.device.delay()
        if self.device(resourceId="com.tct.fmradio.bb:id/play_stop").description == "Stop":
            self.logger.debug("FM working....")
            self.device.delay(fm_play_time)
            if self.device(resourceId="com.tct.fmradio.bb:id/play_stop").description == "Stop":
                self.logger.info("play radio 30 min success")
                self.exit()
                return True
            else:
                self.logger.info("play radio 30 min failed")
                self.save_fail_img()
                self.exit()
                return False
        else:
            self.logger.info("FM not working")
            self.save_fail_img()
            self.exit()
            return False


if __name__ == '__main__':
    a = FM("2cf8e42d", "fm")
    a.switch("Stop")
