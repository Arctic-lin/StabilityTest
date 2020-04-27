# -*- coding: UTF-8 -*-
__author__ = '93760'
from common import *
from settings import Settings


class LockScreen(Common):
    def __init__(self, device, mod, sdevice=None):
        Common.__init__(self, device, mod, sdevice)
        self.set = Settings(self.device, "lock_set")

    def enter(self):
        return self.set.enter_settings("Security")

    def swipe_screen(self):
        self.device.sleep()
        self.logger.info("device sleep")
        self.device.delay()
        self.device.wakeup()
        self.logger.info("device awake")
        self.device.delay(5)
        self.logger.info("swipe screen")
        self.device.swipe(380, 1900, 380, 700, 10)
        self.device.delay()
        self.logger.info("Verify")
        return self.is_launcher_home()

    def lock_screen(self, lock_type, password=None):
        self.logger.info("%s lock screen" % lock_type)
        self.device.press.home()
        if self.swipe_screen():
            return True
        self.device.delay(1)
        if lock_type != "Swipe":
            self.logger.info("enter %s password %s" % (lock_type, password))
            if lock_type == 'Pattern':
                self.unlock_pattern()
            elif lock_type == "PIN":
                self.input_pwd(str(password))
                # self.device(resourceId="com.android.systemui:id/key_enter").click()
            else:
                self.device(resourceId="com.android.systemui:id/passwordEntry").set_text(password)
                self.device.press.enter()
        if self.is_launcher_home():
            self.logger.info("%s lock screen success" % lock_type)
            return True
        self.logger.info("%s lock screen fail" % lock_type)
        self.save_fail_img()
        return False

    def is_launcher_home(self):
        home_id = self.device(text='Camera')
        return home_id.wait.exists(timeout=2000)

    def switch_lock_to_none(self, lock_type, password=None):
        """Swipe PIN Password
        """
        self.logger.info("switch %s lock type to None" % lock_type)
        self.enter()
        self.device(text="Screen lock").click()
        self.device.delay()
        if lock_type == "Swipe":
            self.device(text="None").click()
        elif lock_type == "Pattern":
            self.input_pattern()
            self.device(text="None").click()
            self.device.delay(1)
            self.device(text="YES, REMOVE").click()
        else:
            self.device(resourceId="com.android.settings:id/password_entry").set_text(password)
            self.device.press.enter()
            self.device(text="None").click()
            self.device.delay(1)
            self.device(text="YES, REMOVE").click()
        if self.device(text="None").wait.exists(timeout=2000):
            self.logger.info("switch %s lock type to None success" % lock_type)
            self.back_to_home()
            return True
        self.logger.info("switch %s lock type to None failed" % lock_type)
        self.save_fail_img()
        self.back_to_home()
        return False

    def switch_lock_to_lock(self, lock_type, password=None):
        """Swipe PIN Password
        """
        self.logger.info("switch None lock to %s lock type" % lock_type)
        self.enter()
        self.device(text="Screen lock").click()
        self.device(text=lock_type).click()
        self.device.delay()
        if lock_type == 'Pattern':
            self.input_pattern()
            self.device(resourceId="com.android.settings:id/footerRightButton").click()
            self.device.delay(2)
            self.input_pattern()
            self.device(resourceId="com.android.settings:id/footerRightButton").click()
            self.device.delay()
            if self.device(text="DONE").exists:
                self.device(text="DONE").click.wait()
            elif self.device(resourceId="com.android.settings:id/redaction_done_button").exists:
                self.device(resourceId="com.android.settings:id/redaction_done_button").click()
            else:
                self.logger.debug("can not found DONE")

        elif lock_type != "Swipe":
            if self.device(text="No thanks").exists:
                self.device(text="No thanks").click()
            self.device(resourceId="com.android.settings:id/password_entry").set_text(password)
            self.device.press.enter()
            self.device(resourceId="com.android.settings:id/password_entry").set_text(password)
            self.device.press.enter()
            self.device.delay()
            if self.device(text="DONE").exists:
                self.device(text="DONE").click.wait()
            elif self.device(resourceId="com.android.settings:id/redaction_done_button").exists:
                self.device(resourceId="com.android.settings:id/redaction_done_button").click()
            else:
                self.logger.debug("can not found DONE")

        if self.device(text=lock_type).wait.exists(timeout=2000):
            self.logger.info("switch None lock to %s lock type success" % lock_type)
            self.back_to_home()
            return True
        self.logger.info("switch None lock to %s lock type failed" % lock_type)
        self.save_fail_img()
        self.back_to_home()
        return False

    def input_pattern(self):
        points = [(364, 670), (540, 670), (540, 854), (540, 1036), (364, 1036)]
        steps = 50
        self.device.swipePoints(points, steps)
        self.device.delay()

    def unlock_pattern(self):
        if self.isMILAN_GL:
            points = [(362, 852), (540, 852), (540, 1032), (540, 1212), (362, 1212)]
        elif self.isMILAN_EEA:
            points = [(362, 852), (540, 852), (540, 1032), (540, 1212), (362, 1212)]
        else:
            points = [(362, 852), (540, 852), (540, 1032), (540, 1212), (362, 1212)]
        steps = 50
        self.device.swipePoints(points, steps)
        self.device.delay()

    def switch_wallpaper(self, index=0):
        self.logger.info("switch wallpaper to %d" % (index % 2))
        self.device.press.home()
        # self.device.swipe(1000, 900, 300, 900, steps=10)
        self.device.delay(1)
        if self.isMILAN_GL:
            self.device.long_click(368, 720)
        elif self.isMILAN_EEA:
            self.device.long_click(368, 720)
        else:
            self.device.long_click(540, 900)
        self.device.delay(2)
        if self.device (resourceId='com.tcl.android.launcher:id/wallpaper_button').exists:
            self.device(resourceId='com.tcl.android.launcher:id/wallpaper_button').click()
        # self.device.delay(2)
        # # self.device(resourceId="com.tcl.android.launcher:id/static_wallpapers").click()
        # # self.device.delay()
        # sel wallpaper
        index = random.randint(0, 6)
        self.device.delay (4)
        if self.device(resourceId="com.tcl.android.launcher:id/wallpaper_thumbnails_item",index=index).exists:
            self.device(resourceId="com.tcl.android.launcher:id/wallpaper_thumbnails_item",index=index).click()
        self.device.delay ()
        if self.device(resourceId='com.tcl.android.launcher:id/set_wallpaper_button').exists:
            self.device(resourceId='com.tcl.android.launcher:id/set_wallpaper_button').click()
            self.device.delay(2)

        # set wallpaper to both or /home/lock only
        if self.device(resourceId="com.tcl.android.launcher:id/set_both").wait.exists(timeout=2000):
            self.device(resourceId="com.tcl.android.launcher:id/set_both").click()
            self.device.delay(1)

        if self.is_launcher_home():
            self.logger.info("switch wallpaper to %d success" % index)
            return True
        self.logger.info("switch wallpaper to %d failed" % index)
        self.save_fail_img()
        return False

    def input_pwd(self, password):
        for char in password:
            self.device(text=char, resourceId="com.android.systemui:id/digit_text").click()


if __name__ == "__main__":
    a = LockScreen("ed505a05", "LockScreen")
    # a.enter()
    a.switch_wallpaper()
    # a.switch_lock_to_none('Pattern')
    # a.lock_screen("Password", "aaaa")
    # a.switch_lock_to_none("Password", "aaaa")
