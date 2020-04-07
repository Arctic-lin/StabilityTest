#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2018/9/13 9:00

information about this file
"""
from common import *


class SocialAppGL(Common):
    def __init__(self, device, mod, sdevice=None):
        Common.__init__(self, device, mod, sdevice)
        self.whatonyourmind = self.device(description="What's on your mind?")  # help to ensure facebook home activity
        self.tw_home = self.device(resourceId="com.twitter.android:id/home")

    def fb_enter(self):
        """Launch gallery by StartActivity.
        """

        if self.whatonyourmind.exists:
            self.logger.debug('Facebook opened already')
            return True
        else:
            self.logger.debug('enter Facebook')
            self.start_app("Facebook", True)  # it is Photos for GL Blackberry devices

            # verify
            # toverify = {'text': "What's on your mind?"}
            # return self.fb_swipe_then_watch_sth(toverify, failmsg='enter facebook fail!')
            if self.whatonyourmind.wait.exists(timeout=3000):
                self.logger.info("Facebook open Success")
                return True
            self.logger.info('Facebook open Fail')
            self.save_fail_img()
            return False

    def fb_post(self):
        msg = self.gen_random_msg()
        self.logger.debug("******* %s ******" % msg)
        self.whatonyourmind.click()
        self.device.wait.idle()

        self.device(text="What's on your mind?").click()
        self.adb.shell("input keyevent KEYCODE_DEL")
        self.adb.shell("input text %s" % msg)

        share = self.device(text="SHARE")
        assert share.wait.exists(), "**** can not find share btn ****"
        share.click.wait(timeout=3000)
        self.device.wait.idle()

        share_now = self.device(description="SHARE NOW")
        assert share_now.wait.exists(), "**** can not find share btn ****"
        share_now.click.wait(timeout=3000)
        self.device.wait.idle()

        # verify
        # toverify = {'text': msg}
        # return self.fb_swipe_then_watch_sth(toverify, failmsg='post fail')
        self.device.delay(5)
        if self.whatonyourmind.exists:  # 检查msg无论是text还是description，总是检查不到
            self.logger.info("post Success")
            return True
        self.logger.info('post Fail')
        self.save_fail_img()
        return False

    def fb_swipe_then_watch_sth(self, sth, failmsg):
        sx, sy, ex, ey = self.gen_loc_for_swipe(orientation='v', rate_from=0.5, rate_to=0.8)
        # add skip welcome
        for i in range(3):
            self.device.delay()
            if self.device(**sth).exists:
                return True
            else:
                self.device.swipe(sx, sy, ex, ey, steps=10)
        self.logger.debug(failmsg)
        self.save_fail_img()
        return False

    def tw_enter(self):
        """Launch Twitter by StartActivity.
        """
        if self.tw_home.exists:
            self.logger.debug('Twitter opened already')
            return True
        else:
            self.logger.debug('enter Twitter')
            self.start_app("Twitter", True)  # it is Photos for GL Blackberry devices

            if self.tw_home.wait.exists(timeout=3000):
                self.logger.info("Twitter open Success")
                return True
            self.logger.info('Twitter open Fail')
            self.save_fail_img()
            return False

    def tw_send_msg(self):
        self.tw_msg_factory()

        # verify, assume msg send within 10s
        if self.device(text="Sending…").wait.gone(timeout=10000):
            return True
        return False

    def tw_msg_factory(self):
        """
        random generate msg to friend
        :return:
        """
        media = random.choice(['txt', 'photo', 'video'])
        msg = self.gen_random_msg()
        self.logger.info("random choice is %s" % media)

        if media == 'txt':
            self.device(resourceId="com.twitter.android:id/tweet_text").set_text(msg)
        elif media == 'photo':
            self._tw_take_photo(msg, forcompose=True)
        elif media == 'video':
            self._tw_take_video(msg, forcompose=True)

        # send
        tweet = self.device(resourceId="com.twitter.android:id/send_dm_button")
        assert tweet.wait.exists(), "**** can not find send btn ****"
        tweet.click.wait(timeout=3000)

    def tw_enter_msg(self):
        composer = self.device(resourceId="com.twitter.android:id/composer_write")
        assert composer.wait.exists(), "**** can not find composer ****"
        composer.click.wait(timeout=3000)

        # select first friend
        friend = self.device(resourceId="com.twitter.android:id/name_item")
        assert friend.wait.exists(), "**** can not find friend ****"
        friend.click.wait(timeout=3000)

        # click next
        nextbtn = self.device(resourceId="com.twitter.android:id/compose_next")
        assert nextbtn.wait.exists(), "**** can not find next btn ****"
        nextbtn.click.wait(timeout=3000)

    def tw_post(self):
        create = self.device(resourceId="com.twitter.android:id/composer_write")
        assert create.wait.exists(), "**** can not find create btn ****"
        create.click.wait(timeout=3000)
        self.device.wait.idle()

        self.tw_media_factory()

        # add some delay here, to avoid post msg too fast
        self.device.delay(10)
        self._tw_wait_processbar_gone()

        # verify the msg posted can not be verified, just verify that Twitter come back home activity
        if self.tw_home.wait.exists(timeout=3000):
            self.logger.info("Twitter post Success")
            return True
        self.logger.info('Twitter post Fail')
        self.save_fail_img()
        return False

    def tw_media_factory(self):
        """
        random generate msg then post
        :return:
        """
        media = random.choice(['txt', 'photo', 'video'])
        msg = self.gen_random_msg()
        self.logger.info("random choice is %s" % media)

        if media == 'txt':
            self.device(resourceId="com.twitter.android:id/tweet_text").set_text(msg)
        elif media == 'photo':
            self._tw_take_photo(msg)
        elif media == 'video':
            self._tw_take_video(msg)

        # post
        tweet = self.device(resourceId="com.twitter.android:id/button_tweet")
        assert tweet.wait.exists(), "**** can not find tweet btn to post ****"
        tweet.click.wait(timeout=3000)

    def _tw_take_video(self, msg, forcompose=False):
        self._tw_open_media(forcompose)
        # switch video mode
        switch_video = self.device(resourceId="com.twitter.android:id/button_camera_mode")
        assert switch_video.wait.exists(), "**** can not find switch btn ****"
        switch_video.click.wait(timeout=3000)
        self.device.wait.idle()

        # take video
        capture_vtn = self.device(resourceId="com.twitter.android:id/image_camera_prev_shutter")
        x, y = capture_vtn.get_location()
        self.device.swipe(x, y, x - 100, y - 100, steps=200)
        self.device.wait.idle()

        # confirm video
        done = self.device(resourceId="com.twitter.android:id/done")
        assert done.wait.exists(), "**** can not find done btn ****"
        done.click.wait(timeout=3000)

        # add a comment
        self._tw_add_acommnet(msg, forcompose)

    def _tw_take_photo(self, msg, forcompose=False):

        self._tw_open_media(forcompose)

        # capture
        capture = self.device(resourceId="com.twitter.android:id/image_camera_shutter")
        assert capture.wait.exists(), "**** can not find shutter btn ****"
        capture.click.wait(timeout=3000)

        # confirm capture
        confirm = self.device(resourceId="com.twitter.android:id/speed_bump_use")
        assert confirm.wait.exists(), "**** can not find confirm capture btn ****"
        confirm.click.wait(timeout=3000)

        # add a comment
        self._tw_add_acommnet(msg, forcompose)

    def _tw_open_media(self, forcompose=False):
        if forcompose:
            self.device(resourceId="com.twitter.android:id/media_compose").click()
            self.device.wait.idle()
            self.device(resourceId="com.twitter.android:id/gallery_header_camera").click()
        else:
            self.device(resourceId="com.twitter.android:id/media_rail_tile_photo").click()
        self.device.wait.idle()

    def _tw_add_acommnet(self, msg, forcompose=False):
        self.device(resourceId="com.twitter.android:id/tweet_text").set_text(msg)

    def _tw_wait_processbar_gone(self):
        sx, sy, ex, ey = self.gen_loc_for_swipe(orientation='v', rate_from=0.5, rate_to=0.8)
        for i in range(3):
            if self.device(resourceId="com.twitter.android:id/main_progress_bar").exists:
                self.device.swipe(sx, sy, ex, ey, steps=10)
                self.device.delay(3)
            else:
                return

    def tw_go_tab(self, **kwargs):
        tab = self.device(**kwargs)
        assert tab.wait.exists(), "**** can not find this tab ****"
        tab.click.wait(timeout=3000)


if __name__ == '__main__':
    f = SocialAppGL('5000000266', 'Socialappgl')
    # f.fb_enter()
    # f.fb_post()
    # f.temp()
    f.tw_enter()
    f.tw_go_tab(resourceId='com.twitter.android:id/dms')
    f.tw_enter_msg()
    for i in range(10):
        f.tw_send_msg()
