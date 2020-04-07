#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2018/9/13 9:01

information about this file
"""
from common import *


class WeChat(Common):
    def __init__(self, device, mod, sdevice=None):
        Common.__init__(self, device, mod, sdevice)
        self.wechat = self.device(resourceId="com.tencent.mm:id/cdj", text="WeChat")
        self.contacts = self.device(resourceId="com.tencent.mm:id/cdj", text="Contacts")
        self.discover = self.device(resourceId="com.tencent.mm:id/cdj", text="Discover")

        self.capture = self.device(resourceId="com.tencent.mm:id/cg4")

    def enter(self):
        if self.wechat.exists:
            self.logger.info("webchat opened alread")
            return True
        else:
            self.logger.debug('enter wechat')
            self.start_app("WeChat", True)  # it is Photos for GL Blackberry devices

            if self.wechat.wait.exists(timeout=3000):
                self.logger.info("WeChat open Success")
                return True
            self.logger.info('WeChat open Fail')
            self.save_fail_img()
            return False

    def wc_post(self):
        # click camera icon
        camerabtn = self.device(resourceId="com.tencent.mm:id/hh")
        assert camerabtn.wait.exists(), "**** can not find camera btn ****"
        camerabtn.click.wait(timeout=3000)
        self.device.wait.idle()

        # confirm camera selection
        confirm = self.device(resourceId="com.tencent.mm:id/ge", text='Camera')
        assert confirm.wait.exists(), "**** can not find camera confirm menu ****"
        confirm.click.wait(timeout=3000)
        self.device.wait.idle()

        # take photo or video
        self.media_factory()

        # add say something, then publish
        self.say_something()
        self.click_publish()

        # delay
        self.device.delay(30)

        # can not verify the msg publish, just assert it come back to moment activity
        if camerabtn.wait.exists():
            self.logger.info("Wechat post pass")
            return True
        else:
            self.logger.info("Wechat post fail")
            return False

    def wc_msg(self):
        choice = random.choice(['txt', 'multi'])

        if choice == 'txt':
            self.logger.info("got choice, %s" % choice)
            msg = self.gen_random_msg()
            self.device(resourceId="com.tencent.mm:id/ac8").set_text(msg)
            self.device.wait.idle()

            # send
            send = self.device(text="Send")
            assert send.wait.exists(), "**** can not find send btn ****"
            send.click.wait(timeout=3000)

        elif choice == 'multi':
            # click '+' icon
            self.click_hide_more_func()

            # click camera
            camera = self.device(text="Camera")
            assert camera.wait.exists(), "**** can not find camera btn ****"
            camera.click.wait(timeout=3000)
            self.device.wait.idle()

            self.media_factory()

            self.device.press.back()

        # delay some time, avoid send msg too fast
        self.device.delay(30)

        return True

    def go_to_tab(self, tab):
        assert tab.wait.exists(), "**** can not find target ****"
        tab.click.wait(timeout=3000)

    def media_factory(self):
        # select font camera
        camera_switcher = self.device(resourceId="com.tencent.mm:id/vu")
        assert camera_switcher.wait.exists(), "**** can not find camera switcher ****"
        camera_switcher.click.wait(timeout=3000)
        self.device.wait.idle()

        choice = random.choice(['photo', 'video'])
        self.logger.info("media choice, %s" % choice)

        if choice == 'photo':
            self.take_photo()
        elif choice == 'video':
            self.take_video()

    def take_photo(self):
        # click capture btn
        assert self.capture.wait.exists(), "**** can not find capture btn ****"
        self.capture.click.wait(timeout=3000)
        self.device.wait.idle()

        self.confirm_media_selection()

    def take_video(self):
        # long click capture btn to take video
        x, y = self.capture.get_location()
        self.device.swipe(x, y, x - 100, y - 100, steps=200)
        self.device.wait.idle()

        self.confirm_media_selection()

    def confirm_media_selection(self):
        # select
        select = self.device(resourceId="com.tencent.mm:id/vr")
        assert select.wait.exists(), "**** can find select btn ****"
        select.click.wait(timeout=3000)
        self.device.wait.idle()

    def say_something(self):
        say_someth = self.device(resourceId="com.tencent.mm:id/djk")
        assert say_someth.wait.exists(), "**** can not find 'say something...'****"
        msg = self.gen_random_msg()
        say_someth.set_text(msg)

    def select_friend(self, name_startswith):
        friend = self.device(textStartsWith=name_startswith)
        assert friend.wait.exists(), "**** can not find friend name ****"
        friend.click.wait(timeout=3000)
        self.device.wait.idle()

    def click_messages(self):
        messages = self.device(resourceId="com.tencent.mm:id/ap1")
        assert messages.wait.exists(), "**** can not find messages btn ****"
        messages.click.wait(timeout=3000)
        self.device.wait.idle()

    def click_monents(self):
        monments = self.device(text="Moments")
        assert monments.wait.exists(), "**** can not find monments ****"
        monments.click.wait(timeout=3000)
        self.device.wait.idle()

    def click_publish(self):
        publish = self.device(resourceId="com.tencent.mm:id/hg")
        assert publish.wait.exists(), "**** can not find publish btn ****"
        publish.click.wait(timeout=3000)
        self.device.wait.idle()

    def click_hide_more_func(self):
        more = self.device(resourceId="com.tencent.mm:id/acc")
        assert more.wait.exists(), "**** can not find more func btn ****"
        more.click.wait(timeout=3000)
        self.device.wait.idle()


if __name__ == '__main__':
    case = WeChat('5000000266', 'Socialappcn')
    # case.enter()
    # case.go_to_tab(case.contacts)
    # case.select_friend(name_startswith='PT')
    # case.click_messages()
    for i in range(10):
        case.wc_msg()
