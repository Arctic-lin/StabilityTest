#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: maps.py
@time: 11/6/2017 10:27 AM

information about this file
"""
from common import *


class GoogleMap(Common):
    package = 'com.google.android.apps.maps'
    name = 'Maps'

    def setup(self):
        self.clear(self.package)
        self.enter()

    def enter(self):
        """Launch google maps
        """
        self.logger.debug('enter google maps')
        self.start_app("Maps")
        self.device.wait("idle")
        if self.device(text="SKIP").wait.exists():
            self.device(text="SKIP").click.wait()
        if self.device(text="TURN OFF").wait.exists():
            self.device(text="TURN OFF").click.wait()
        return self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").wait.exists()

    def back_to_maps(self):
        self.logger.info("Back to maps.")
        for i in range(4):
            if self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").wait.exists(
                    timeout=1000):
                self.device(description="Clear").click()
                return
            else:
                self.device.press.back()
        self.enter()
        for i in range(4):
            if self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").wait.exists(
                    timeout=1000):
                self.device(description="Clear").click()
                return
            else:
                self.device.press.back()

    def navigation(self):
        """determine whether the navigation, return True/False
        """
        if self.device(description="Close navigation").wait.exists(timeout=5000):
            self.logger.info("Navigation....")
            return True
        self.logger.info("Navigation fail!!!")
        self.save_fail_img()
        return False

    def maps_navigation(self):
        """start google maps, enter the navigation
        """
        # destination = Configs("common").get("destination", "Maps")
        destination = "Ningbo Research & Development Park"
        self.logger.debug("Search: %s" % destination)
        self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_text_box").click.wait()
        self.device(resourceId="com.google.android.apps.maps:id/search_omnibox_edit_text").set_text(destination)
        self.device.wait("idle")
        self.device.press.enter()
        # if self.device(text=destination).wait.exists():
        #     self.device(text=destination).click()
        self.logger.debug("Start navigation to: %s" % destination)
        self.device.wait("idle")

        assert self.device(text="Directions").wait.exists(timeout=30000)
        self.device(text="Directions").click.wait()
        if self.device(text="GOT IT").wait.exists(timeout=3000):
            self.device(text="GOT IT").click.wait()
        if self.device(description="Directions").wait.exists():
            self.device(description="Directions").click.wait()
        if self.device(text="OK").exists:
            self.device(text="OK").click.wait()
        self.device.delay(5)
        # todo: verify distance?
        self.device(text="START").click.wait(timeout=3000)
        if self.device(text="GOT IT").wait.exists(timeout=3000):
            self.device(text="GOT IT").click()
        return self.navigation()

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


if __name__ == '__main__':
    a = GoogleMap("1163805830", "Maps")
    a.enter()
    a.maps_navigation()
    # a.back_navigation()
    # a.close_location()
