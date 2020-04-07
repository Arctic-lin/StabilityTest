# -*- coding: utf-8 -*-
"""Email library """

import traceback

from common import Common


class Gmail(Common):
    """Provide common functions involved email."""

    def __init__(self, device, log_name):
        Common.__init__(self, device, log_name)
        self.appconfig.set_section("Gmail")
        # self.mail_with_attachment = 'test mail with attachment'
        # self.mail_without_attachment = 'test mail without attachment'
        self.new_mail_btn = self.device(resourceId="com.google.android.gm:id/compose_button")
        self.in_menu = self.device(resourceId="com.google.android.gm:id/product_name", text='Gmail')
        self.menu_btn = self.device(description="Open navigation drawer")

    def enter(self):
        if self.is_home():
            self.logger.info("Gmail opened already")
            return True
        self.start_app('Gmail')

        # verify
        if self.is_home():
            self.logger.info("open gmail done")
            return True
        self.logger.error("******* open gmail fail ******")
        return False

    def open_menu(self):
        self.logger.info("open menu")
        self.menu_btn.click()
        self.device.wait.idle()

    def enter_item(self, name):
        self.logger.info("enter menu item {}".format(name))

        if self.device(text=name, resourceId="com.google.android.gm:id/name").exists:
            self.logger.debug("%s exists" % name)
        elif self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.to(text=name)

        self.device(text=name, resourceId="com.google.android.gm:id/name").click()
        self.device.wait.idle()
        self.logger.info("enter menu item {} successfully".format(name))

    def _set_mail_to(self, addr=None):
        # self.device(resourceId="com.google.android.gm:id/to").click()
        self.device(resourceId="com.google.android.gm:id/to").set_text(addr)
        self.device.wait.idle()

    def _set_mail_subject(self, subject):
        self.device(resourceId="com.google.android.gm:id/subject").set_text(subject)
        self.device.wait.idle()

    def _set_mail_body(self, body=None):
        content = 'This_is_test_mail,do_not_reply,thank_you!' if body is None else body
        self.device(text="Compose email").click()
        self.device.wait.idle()
        self.adb.input(content)
        self.device.wait.idle()

    def _set_attachment(self, file_name="10010.vcf"):
        """
        从file manager跟目录中选取
        :param file_name: 需要放在内部存储的跟目录下
        :return:
        """
        self.device(resourceId="com.google.android.gm:id/add_attachment").click()
        self.device.wait.idle()

        self.device(text="Attach file").click()
        self.device.wait.idle()
        
        self.device(description="Show roots").click()
        self.device.wait.idle()

        self.device(text="File Manager",index=0).click()#Gallery,File Manager
        self.device.wait.idle()

        self.device(text="Internal storage").click()
        self.device.wait.idle()

        self.device(scrollable=True).scroll.vert.to(text=file_name)
        self.device.wait.idle()

        # self.device(text="StabilityResource").click()

        self.device(text=file_name).click()
        self.device.wait.idle()

    def _click_send(self):
        self.logger.info("click sent btn")
        self.device(resourceId="com.google.android.gm:id/send").click()
        self.device.wait.idle()

    def is_home(self):
        if self.new_mail_btn.exists:
            return True
        # self.save_fail_img()
        return False

    def is_menu_opened(self):
        if self.in_menu.exists:
            return True
        # self.save_fail_img()
        return False

    def is_mail_exist(self, subject):
        if self.device(text=subject).exists:
            return True
        return False

    def is_outbox_empty(self):
        if self.device(text="Nothing in Outbox").exists:
            return True
        self.logger.debug("out box is not empty")
        return False

    def is_primary_empty(self):
        if self.device(text="Nothing in Primary").exists:
            return True
        return False

    def is_sent_empty(self):
        if self.device(text="Nothing in Sent").exists:
            return True
        elif self.device(textContains="unsent in Outbox").wait.exists(timeout=3000):  # 网络关系，邮件未发送 bypass
            self.device(text="Dismiss").click()
            return True
        return False

    def verify_mail_sent(self, subject):
        """
        verify mail sent or not, just check outbox
        :param subject:
        :return:
        """
        self.logger.info("verify mail sent in outbox")
        assert self.back_to_mail_menu(), 'can not back to menu'
        self.open_menu()
        self.enter_item('Outbox')
        self.device.wait.idle()

        # timeout 3min
        for i in range(20):
            if self.is_outbox_empty():
                self.logger.info("send mail {} successfully".format(subject))
                return True
            self.logger.debug("outbox is not empty,continue")
            self.device.delay(5)

        self.delete_mail(5)
        self.logger.info("send mail {} failed".format(subject))
        self.save_fail_img()
        return False

    def empty_trash(self):
        try:
            self.open_menu()
            self.enter_item('Trash')
            if self.device(text="Empty trash now").ext5:
                self.device(text="Empty trash now").click()
            if self.device(text="Empty",resourceId="android:id/button1").ext5:
                self.device(text="Empty",resourceId="android:id/button1").click()
        except:
            self.logger.warning(traceback.format_exc())

    def del_all_sent(self):
        """
        del all mail in sent box
        :return:
        """
        try:
            assert self.back_to_mail_menu(), 'can not back to menu'
            self.open_menu()
            self.enter_item('Sent')
            self.device.wait.idle()

            if self.is_sent_empty():
                return True
            self.delete_mail(100)
            assert self.is_sent_empty(), "******* del sent box fail ******"
        except:
            self.logger.warning(traceback.format_exc())
            self.save_fail_img()
        return False

    def delete_mail(self, times):
        for i in range(times):
            if self.is_outbox_empty():
                return True
            parent = self.device(resourceId="com.google.android.gm:id/thread_list_view")
            child_count = parent.childCount
            for x in range(child_count):
                item = parent.child(resourceId="com.google.android.gm:id/viewified_conversation_item_view",
                                    index=x).child(resourceId="com.google.android.gm:id/contact_image")
                if item.exists:
                    item.click()
                    x += 1
                    self.logger.debug("select mail %d times" % x)

            # if self.device(resourceId="com.google.android.gm:id/contact_image").ext5:
            #     self.device(resourceId="com.google.android.gm:id/contact_image").click()
            if self.device(description="Delete").exists:  # delete button is invalid
                self.device(description="Delete").click.wait(timeout=3000)
            elif self.device(resourceId="com.google.android.gm:id/discard_outbox").exists:
                self.device(resourceId="com.google.android.gm:id/discard_outbox").click.wait(timeout=3000)
            else:
                self.logger.debug("delete mail failed")
                break

            i += 1
            self.logger.debug("delete sent box %d times" % i)

    def back_to_mail_menu(self):
        """
        back to the activity with menu btn,
        restart gmail if press back 10 times
        :return:
        """
        for i in range(10):
            self.device.delay(1)
            if self.menu_btn.exists:
                return True
        else:
            self.back_to_home()
            self.enter()

        if self.menu_btn.exists:
            return True

        return False

    def create_mail_and_sent(self, mailto, with_attachment):
        """
        create mail and sent, then verify
        :param mailto:
        :param with_attachment:
        :return:
        """
        assert self.new_mail_btn.exists, 'can not find new email btn'

        self.new_mail_btn.click()
        self.device.wait.idle()

        # in edit mail activity
        self._set_mail_to(mailto)
        subject = self.gen_random_subject()
        self._set_mail_subject(subject)
        self._set_mail_body()

        if with_attachment:
            self._set_attachment()

        # send
        self._click_send()

        # 网络原因经常发不出去，在发件箱中排队，当在中国测试时，直接返回，不验证发送
        if self.is_testing_in_china:
            return True

        # verify
        self.device.delay(timeout=5)
        if self.verify_mail_sent(subject):
            return True

        return False

    def save_draft_and_sent(self, mailto):
        """
        save draft and sent it
        :param mailto:
        :return:
        """
        self.logger.info("test save draft")
        assert self.new_mail_btn.exists, 'can not find new email btn'

        self.new_mail_btn.click()
        self.device.wait.idle()

        # in edit mail activity
        self._set_mail_to(mailto)
        subject = self.gen_random_subject()
        self._set_mail_subject(subject)
        self._set_mail_body()

        # save mail to draft
        self.logger.info("press back twice to save draft")
        self.device.press.back()
        self.device.press.back()

        
        # sent draft
        self.sent_draft(subject)

        # verify
        self.device.delay(timeout=5)
        if self.verify_mail_sent(subject):
            return True

        return False

    def sent_draft(self, subject):
        """
        go to draft and sent the mail with given subject
        :param subject:
        :return:
        """
        self.logger.info("send draft")
        assert self.back_to_mail_menu(), 'can not find new email btn'

        self.open_menu()
        self.enter_item('Drafts')

        self.device.delay(2)
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.to(descriptionContains=subject)

        self.device(descriptionContains=subject).click()
        self.device.wait.idle()

        self.device(resourceId="com.google.android.gm:id/edit_draft").click()
        self.device.wait.idle()

        self._click_send()
        self.device.wait.idle()

    def setup(self):
        self.enter()
        self.device.delay(5)
        el = self.device(resourceId="com.google.android.gm:id/welcome_tour_got_it")
        el2 = self.device(resourceId="com.google.android.gm:id/action_done")
        el3 = self.device(resourceId="com.google.android.gm:id/gm_dismiss_button")
        el4 = self.device(resourceId="com.google.android.gm:id/gm_dismiss_button")
        el5 = self.device(resourceId="com.google.android.gm:id/dismiss_icon")
        self.click_all_items_if_exists(2000, el, el2, el3, el4,el5,el5)
        self.device.delay(2)
        self.back_to_home()
