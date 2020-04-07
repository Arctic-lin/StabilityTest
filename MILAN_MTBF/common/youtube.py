#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: youtube.py
@time: 11/3/2017 5:29 PM

information about this file
"""
from common import *


class YouTube(Common):
    """Provide common functions involved YouTube."""

    def enter(self, wait_load_completed=False):
        """
        enter youtube
        :return:
        """
        self.logger.info("start YouTube")
        if self.device(description="Search").wait.exists(timeout=3000):
            self.logger.info("youtube started")
            return
        self.start_app("YouTube")
        assert self.device(description="Search").wait.exists(timeout=5000)

        if wait_load_completed:
            assert self.device(resourceId="com.google.android.youtube:id/thumbnail").wait.exists(timeout=3000)

    def verify_account_login(self, account):
        """
        verify account is enrolled or not
        :param account:
        :return:
        """
        topbar = self.device(resourceId="com.google.android.youtube:id/mobile_topbar_avatar")
        assert topbar.wait.exists(), "******** can not find topbar  ********"
        topbar.click.wait(timeout=3000)

        switch_account = self.device(text="Switch account")
        if not switch_account.wait.exists():
            topbar.click.wait(timeout=3000)
        assert switch_account.wait.exists(), "******** can not find switch account  ********"
        switch_account.click.wait(timeout=3000)

        assert self.device(text=account).wait.exists(
            timeout=5000), "******** can not find account: %s  ********" % account


if __name__ == '__main__':
    a = YouTube("80c08ac6", "YouTube")
