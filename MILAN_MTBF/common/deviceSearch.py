#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: deviceSearch.py
@time: 11/8/2017 7:14 PM

information about this file
"""

from common import *


class DeviceSearch(Common):
    """
    common method for BB app device search
    """

    def enter(self):
        self.logger.info('enter Device search')
        self.start_app("Device Search")

        if self.device(text="SKIP INTRO").wait.exists(timeout=3000):
            self.device(text="SKIP INTRO").click.wait()

        return self.is_home()

    def is_home(self):
        return self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").wait.exists(timeout=3000)

    def search_songs(self, param="Madness"):
        """
        search some thing
        :param param:
        :return:
        """
        self.search(param)
        search_ret = self.device(resourceId="com.blackberry.universalsearch:id/text_1", text=param)
        assert search_ret.wait.exists(), "******** can not find any song matched  ********"
        search_ret.click.wait()

        if self.device(text="Open with").exists:
            self.device(resourceId="android:id/text1").click.wait()
            self.device(text="ALWAYS").click.wait()
        self.device.delay()
        # info = self.device.dump()
        # assert com.google.android.music:id/play_pause_button
        assert self.device(resourceId="com.google.android.music:id/play_pause_button").wait.exists(
            timeout=10000), "***** song do not playing *****"
        self.logger.debug("search songs %s successfully" % param)

    def search_contacts(self, param="Lewis Hamilton"):
        self.search(param)
        search_ret = self.device(resourceId="com.blackberry.universalsearch:id/text_1", text=param)
        assert search_ret.wait.exists(), "******** can not find any contact matched  ********"
        self.logger.debug("search contact %s successfully" % param)

    def search(self, param):
        assert self.is_home()
        self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").set_text(param)
        self.device.delay()


if __name__ == '__main__':
    a = DeviceSearch("1163805830", "DeviceSearch")
    print a.device.dump(r"c:\recorder.xml")
