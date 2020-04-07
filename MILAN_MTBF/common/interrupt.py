# -*- coding: UTF-8 -*-
"""Maps interrupt library for scripts.
"""
from common import *
from settings import GPS
from telephony import Telephony


class GoogleMapsInterrupt(Common):

    def __init__(self, device, log_name, sdevice=None):
        Common.__init__(self, device, log_name, sdevice=None)
        # self.tel = Telephony(self.device, "maps_tel", self.sdevice)
        self.tel = Telephony(self.device, "maps_tel")   # WD, remove sdevice
        self.gps = GPS(self.device, 'Gps')

    def enter(self):
        """Launch google maps
        """
        self.logger.debug('enter google maps')
        self.start_app("Maps")

        # some times maps go to menu activity, press back
        if self.device(resourceId="com.google.android.apps.maps:id/layers_menu_container").exists:
            self.device.press.back()

        return self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").wait.exists()

    def is_maps_home(self):
        return self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").wait.exists()

    def back_to_maps(self):
        try:
            self.device.press.back()
            self.logger.info("Back to maps.")
            if self.is_maps_home():
                self.logger.info("is maps home.")
                return True

            # some times maps go to menu activity, press back
            if self.device(resourceId="com.google.android.apps.maps:id/layers_menu_container").exists:
                self.device.press.back()

            # found clear btn, click it first
            if self.device(description="Clear").exists:
                self.device(description="Clear").click()

            for i in range(5):
                if not self.device(text="Search here").wait.exists(timeout=1000):
                    self.logger.info("not map home, press back")
                    self.device.press.back()
                else:
                    self.logger.info("back to  maps home success.")
                    return True

            return False
        except:
            pass

    def navigation(self):
        assert self.device(resourceId="com.google.android.apps.maps:id/navigation_time_remaining_label").wait.exists(
            timeout=10000), "Navigation fail!!!"
        return True

    def maps_navigation(self):
        """start google maps, enter the navigation
        """
        for i in range(3):
            try:
                if self._perform_nav():
                    return True
                else:
                    return False
            except AssertionError:
                self.logger.warning(traceback.format_exc())
                self.back_to_home()
                self.clear_background()
                self.enter()

    def _perform_nav(self):
        destination = Configs("common").get("destination", "Maps")
        self.logger.debug("Search: %s" % destination)
        self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").click()
        self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_edit_text").set_text(destination)
        self.device.press.enter()
        self.logger.debug("Start navigation to: %s" % destination)
        self.device.delay(5)
        directions_btn = self.device(resourceId="com.google.android.apps.maps:id/placepage_directions_button")
        if not directions_btn.exists:
            directions_btn = self.device(text="Directions")
        if not directions_btn.exists:
            self.save_fail_img()
        assert directions_btn.exists, "Directions do not found, search out time"
        if directions_btn.exists:
            directions_btn.click.wait(timeout=3000)
            self.device.delay(5)
            if self.device(resourceId="com.google.android.apps.maps:id/directions_startpoint_textbox").exists:
                self.device (resourceId="com.google.android.apps.maps:id/directions_startpoint_textbox").click()
            self.device.delay()
            self.device(text="Your location").click()
            self.device.delay(5)
            self.device(text="Start").click()
            self.logger.info("Clicked START btn")
            self.device.delay()
            # x, y = 906, 2117
            # self.device.click(x, y)
            # self.logger.info("Click start loaction, ({},{})".format(x, y))
            if self.device(text="GOT IT").wait.exists(timeout=3000):
                self.device(text="GOT IT").click()
            return self.navigation()

    def answer_navigation(self):
        """answer call during maps navigation
        """
        if self.tel.s_call():
            self.logger.debug("answer call during maps interrupt success")
            return True
        self.logger.debug("answer call during maps interrupt failed")
        self.save_fail_img()
        return False

    def back_navigation(self):
        """after calling  whether the navigation, return True/False
        """
        self.device.delay(5)
        # self.device(description="End").click()
        self.device.click(540, 1465)
        if self.device(description="End Call").wait.gone():
            self.logger.info("answer call during maps interrupt success")
            return self.navigation()
        self.logger.info("answer call during maps interrupt failed")
        self.save_fail_img()
        return False

    def open_location(self):
        self.logger.info("open location")
        self.start_app("Settings")
        self.device(scrollable=True).scroll.vert.to(text="Location")
        self.device(text="Location").click()
        if self.device(text="OFF").wait.exists():
            self.device(text="OFF").click()
        if self.device(text="ON").wait.exists():
            self.logger.info("open location success")
        else:
            self.logger.info("open location failed")
        self.device.press.back()
        self.device.press.back()

    def close_location(self):
        self.logger.info("close location")
        self.start_app("Settings")
        self.device(scrollable=True).scroll.vert.to(text="Location")
        self.device(text="Location").click()
        if self.device(text="ON").wait.exists():
            self.device(text="ON").click()
        if self.device(text="OFF").wait.exists():
            self.logger.info("close location success")
        else:
            self.logger.info("close location failed")
        self.device.press.back()
        self.device.press.back()

    def setup(self):
        el = self.device(text="Beat the traffic, wherever you go")
        ok = self.device(text='OK')
        for i in range(3):
            self.enter()
            self.device.delay(10)
            if el.wait.exists():
                ok.click()
                self.device.delay()
                return



if __name__ == '__main__':
    a = GoogleMapsInterrupt("80c08ac6", "Maps", "e3a1b0f2")
    # a.open_location()
    # a.enter()
    # a.maps_navigation()
    a.answer_navigation()
    a.back_navigation()
    # a.close_location()
