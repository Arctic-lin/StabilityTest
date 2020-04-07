# -*- coding: utf-8 -*-
"""Email library """

import traceback

from common import Common


class Email(Common):
    def enter(self):
        """Launch email by StartActivity.
        """
        self.logger.debug("Launch email.")
        if self.device(description="Compose button", packageName="com.blackberry.hub").wait.exists(
                timeout=self.timeout):
            return True
        self.start_app("Hub")
        self.device(description="Compose button", packageName="com.blackberry.hub").wait.exists(timeout=self.timeout)
        self.device(resourceId="com.blackberry.hub:id/empty_view").wait.gone(timeout=10000)
        self.device.delay(1)
        return self.device(description="Compose button", packageName="com.blackberry.hub").exists
        # return self.device(description="Compose button", packageName="com.blackberry.hub").wait.exists(
        #     timeout=self.timeout)

    def enter_box(self, box, address=None):
        """enter the box you want
        arg: (str)box --text of the box
        """
        try:
            gmail_receiver = self.config.getstr("Gmail_receiver", "Email", "common")
            self.logger.debug('Gmail_receiver: %s', gmail_receiver)

            self.logger.debug('enter the box: %s', box)
            if not self.device(packageName="com.blackberry.hub").exists:
                self.enter()
            '''if self.device(text=box).exists:
                self.device(text=box).click()
            if self.device(text=box, index=2).exists:
                return True'''
            for i in range(3):
                if self.device(description="Open navigation drawer").wait.exists(timeout=2000):
                    break
                else:
                    self.device.press.back()
                    self.device.delay(1)
                if self.device(packageName="com.blackberry.blackberrylauncher").exists:
                    self.enter()
            self.device(description="Open navigation drawer").click()
            self.device.delay(1)
            if not self.device(text="All Folders").exists:
                if address is not None and gmail_receiver == address:
                    self.logger.debug("address is %s" % address)
                    for loop in range(8):
                        self.logger.debug("check gmail address item %d times" % (loop + 1))
                        emailItem = self.device(resourceId="com.blackberry.hub:id/drawer_tree_list_item_wrapper",
                                                index=loop).child(
                            resourceId="com.blackberry.hub:id/drawer_tree_list_item_container").child(
                            description="ToggleFolderDropDownCollapsed")

                        if emailItem.exists:
                            emailAddressItem = self.device(
                                resourceId="com.blackberry.hub:id/drawer_tree_list_item_wrapper",
                                index=loop).child(
                                resourceId="com.blackberry.hub:id/drawer_tree_list_item_container").child(
                                resourceId="com.blackberry.hub:id/perspective_item").child(
                                resourceId="com.blackberry.hub:id/account_display_name")
                            if gmail_receiver == emailAddressItem.get_text():
                                self.logger.info("get 'gmail:%s' item successfully " % emailAddressItem.get_text())
                                emailItem.click()
                                self.device.delay(1)
                                break

                else:
                    self.logger.debug("enter TCL email item")
                    if self.device(description="ToggleFolderDropDownCollapsed").wait.exists(timeout=5000):
                        self.device(description="ToggleFolderDropDownCollapsed").click()

            self.device(text="All Folders").click.wait(timeout=2000)
            self.device.delay(2)
            if not self.device(text=box).wait.exists(timeout=5000):
                self.logger.warning("Enter box fail: %s" % box)
                self.save_fail_img()
                return False
            self.device(text=box).click()
            self.device.delay(2)
            if self.device(text="Always").exists:
                self.device(text="Always").click()
                self.device.delay(1)
            self.device(resourceId="com.blackberry.hub:id/empty_view").wait.gone(timeout=10000)
            if self.device(text=box, index=1).wait.exists():
                return True
            self.logger.warning("Cannot change to box: %s" % box)
            self.save_fail_img()
            return False
        except:
            pass

    def send_mail(self, send_type, att_flag, address=None):
        """send a email
        arg: send_type(str) forward or reply email
             address(str) email address you want to send
             att_flag(boolean) whether to send with attachments
        """

        if self.device(description='Dismiss tip').exists:
            self.device(description='Dismiss tip').click()
            self.device.delay(1)
        self.logger.debug('create an email')
        self.enter_box('Inbox', "xxx")  # to use TCL email account
        i = self.device(resourceId='com.blackberry.hub:id/list_item_section').count
        if att_flag:
            if self.device(textContains="stability test with one attachment").exists:
                self.device(textContains="stability test with one attachment").click()
            elif self.device(textContains="stability test with an attachment").exists:
                self.device(textContains="stability test with an attachment").click()
            else:
                self.logger.debug('can not find the mail')
        else:
            if self.device(textContains="stability test with no attachment").exists:
                self.device(textContains="stability test with no attachment").click()
            elif self.device(textContains="stability test with no  attachment").exists:
                self.device(textContains="stability test with no  attachment").click()
            else:
                self.logger.debug("can not find the mail")

        if self.device(resourceId="com.blackberry.hub:id/conversation_subject").wait.exists(timeout=15000):
            # self.device(resourceId="com.tct.email:id/overflow").click()
            if self.device(scrollable=True):
                self.device(scrollable=True).scroll.vert.to(description="Forward")
                self.device.delay(1)
            self.device(description=send_type).click()
            self.device.delay(2)
            if send_type == "Forward":
                self.device(className='android.widget.MultiAutoCompleteTextView').set_text(address)
                self.device.delay(1)
                self.device.press.enter()
                self.device.delay(1)
                if not self.device(description='Send', enabled=True).exists:
                    self.logger.info("send btn not clickable, press enter again")
                    self.device.press.enter()
                self.device.delay(2)
            elif send_type == "Reply":
                if self.device(text="Ask for permission").exists:
                    self.device(text="Ask for permission").click.wait()
                    for i in range(10):
                        if self.device(text="Allow").exists:
                            self.device(text="Allow").click.wait()
                        else:
                            break
                # self.device(resourceId='response_container_BBPPID').click()
                self.device.server.adb.shell("input text Reply_email_go_spurs_go")
                self.device.delay(1)
            else:
                # self.device(resourceId='response_container').set_text("Reply email. go spurs go.")
                self.device(resourceId='response_container').click()
                self.device.server.adb.shell("input text Reply_email_go_spurs_go")
                self.device.wait(2)
            self.device(description='Send', enabled=True).click.wait(timeout=2000)
            self.device.delay()
            self.logger.debug('email sending...')

            self.device(resourceId="com.blackberry.hub:id/attach").wait.gone(timeout=70000)
            self.device(resourceId="com.blackberry.hub:id/search_menu_item").wait.exists(timeout=70000)
            self.device.wait("idle")

            self.device.press.back()
            self.device.delay(1)
            if self.device(text="Discard draft?").exists:
                self.device(text='DISCARD').click.wait(timeout=2000)

            # return True
            return self.verify_sending("xxx")  # to use TCL email account
        else:
            self.logger.warning('Cannot open an email')
            self.save_fail_img()
            return False

    def del_mail(self, box, address=None):
        """delete all email of the box
        arg: (str)box --text bof the box
        """
        self.logger.debug('delete the mail of %s' % box)
        self.enter_box(box, address)
        try:
            if self.device(text="No items in this view").exists:
                self.logger.info('no mails in %s', box)
                return True
            for i in range(10):
                x, y = self.device(className="android.support.v7.widget.RecyclerView").child(
                    className='android.view.ViewGroup', index=1).get_location()
                self.device.swipe(x, y, x - 400, y, 200)
                if self.device(text="DELETE").wait.exists():
                    self.device(text="DELETE").click()
                if self.device(text="No items in this view").wait.exists(timeout=5000):
                    self.logger.info("delete the mail of %s success", box)
                    self.device.press.back()
                    return True
        except:
            pass
        self.device.delay(2)
        self.device.press.back()
        self.logger.info("delete the mail of %s failed" % box)
        self.save_fail_img()
        return False

    def create_draft(self, address, loop=0):
        """ save a draft mail
        arg: address(str) draft mail address
             loop(int) draft mail content
        """
        self.device(description="Compose button").click.wait()
        self.device(className='android.widget.MultiAutoCompleteTextView').set_text(address)
        self.device.press.enter()
        self.device(textContains="Subject").set_text("Stability Test %d" % loop)
        self.device.press.enter()
        # self.device(resourceId='response_container').set_text("Reply email. go spurs go.")
        # self.device(resourceId='response_container').click()
        # self.device.server.adb.shell("input text Draft_email_go_spurs_go")

        # you can get attach file to save draft mail
        # self.device(description="Attach file").click.wait()
        # self.logger.info("add test_picture.jpg attach from internal storage")
        # self.device.delay()
        # if not self.device(text="Internal storage", index=1).exists:
        # if not self.device(text="Open from").exists:
        # self.device(description="Show roots").click()
        #     self.device(text="Internal storage").click.wait()
        # if self.device(scrollable=True):
        #     self.device(scrollable=True).scroll.vert.toEnd()
        # if self.device(text="test_picture.jpg").wait.exists(timeout=2000):
        #     self.device(text="test_picture.jpg").click()
        # else:
        #     self.logger.info("not test_picture.jpg  File")
        #     self.device.press.back()

        self.device(description="More options").click.wait()
        self.device(text="Save draft").click()
        self.device.press.back()
        self.enter_box("Drafts")
        if self.device(description="Message draft").wait.exists(timeout=6000):
            self.logger.info("Create draft Stability Test %d success" % loop)
            return True
        else:
            self.logger.info("Create draft Stability Test %d failed" % loop)
            self.save_fail_img()
            return False

    def send_draft(self, loop):
        """send a draft mail
        """
        self.logger.info("send draft Stability Test %d" % loop)
        self.device(className="android.support.v7.widget.RecyclerView").child(
            className='android.view.ViewGroup', index=1).click()
        # if self.device(text="Stability Test %d " % loop).wait.exists(timeout=2000):
        if self.device(resourceId="com.blackberry.hub:id/subjectField").wait.exists(timeout=2000):
            self.logger.info("enter draft Stability Test %d success" % loop)
            # self.device(description="Edit").click.wait(timeout=2000)
            self.device(description="Send").click.wait(timeout=2000)
            self.logger.debug('email sending...')
            self.device(resourceId="com.blackberry.hub:id/attach").wait.gone(timeout=70000)
            self.device(resourceId="com.blackberry.hub:id/search_menu_item").wait.exists(timeout=70000)
            self.device.wait("idle")
            self.device.press.back()
            self.device.delay(2)
            return self.verify_sending()
        else:
            self.logger.info("enter draft Stability Test %d failed" % loop)
            self.save_fail_img()
            return False

    def verify_sending(self, address=None):
        """Validation email sent successfully in 60 seconds
        """
        self.enter_box("Outbox", address)
        if self.device(text="No items in this view").wait.exists(timeout=60000):
            self.logger.debug('email send !!!')
            self.device.press.back()
            return True
        else:
            self.logger.debug('email send fail in 1 min!!!')
            self.save_fail_img()
            self.del_mail("Outbox", address)
            # self.del_mail("Trash")
            # return False
            # todo: ignore send fail.
            return True

            ##################### new method for smoke test ########################################################################

    def enter_and_dismiss(self):
        """
            Launch email and dismiss welcome screen.
        """
        self.logger.debug("Launch email and dismiss welcome screen if needed.")
        self.start_app("Hub")

        # if welcome screen is not exist, call self.enter
        if not self.device(resourceId="com.blackberry.hub:id/slidesOverlayButtonNext").wait.exists(timeout=3000):
            return self.enter()

        while self.device(resourceId="com.blackberry.hub:id/slidesOverlayButtonNext").wait.exists():
            self.device(resourceId="com.blackberry.hub:id/slidesOverlayButtonNext").click()
            self.device.wait.idle()
            if self.device(resourceId="com.blackberry.hub:id/slidesOverlayButtonSkip").wait.exists():
                self.device(resourceId="com.blackberry.hub:id/slidesOverlayButtonSkip").click()
                self.device.wait.idle()
                break

        assert self.device(description="Compose button", packageName="com.blackberry.hub").wait.exists(
            timeout=self.timeout), \
            "hub do not opened or welcome screen do not dismissed"
        return True

    def back_to_hub_home(self):
        """
            back to hub home, if Discard btn found, click it
        """
        self.logger.info("try to back to hub home within 5 steps")
        index = 0
        while (not self.device(description="Open navigation drawer").wait.exists(timeout=2000)) and index < 5:
            self.device.press.back()
            if self.device(text="DISCARD").wait.exists(timeout=1):
                self.device(text="DISCARD").click()
            self.device.delay(1)
            index += 1
        if index >= 5:
            self.save_fail_img()
            self.logger.error("fail to back to hub home")
            return False
        self.logger.info("back to hub home success")
        return True

    def is_hub_home(self):
        """
            check the menu setting bar exist or not, if exist, decide the current activity is hub home
        """
        return self.device(description="Open navigation drawer").wait.exists(timeout=2000)

    def is_account_login(self, account):
        """
            check the given account(email address) exist in menu or not
            @param account: the given account to check

        """
        self.logger.info("verify the given account is login or not")
        if self.is_hub_home():
            self.device(description="Open navigation drawer").click()
            self.device.wait.idle()
            if self.device(text=account).wait.exists(timeout=3000):
                self.logger.info("the given account: %s have logged in." % account)
                return True
            else:
                self.logger.info("the given account: %s  have not logged in" % account)
                return False
        else:
            self.logger.error("do not go to hub home or hub is not opened")
            return False

    def add_account(self, account, pwd, account_type="enterprise"):
        """
            add account
            @param account_type: enterprise(default) or personal. personal means Gmail, it has special step.
            @param pwd: password
            @param account: account(email address) to add

        """
        self.logger.debug("try to add %s account." % account_type)
        self.enter()
        assert self.back_to_hub_home(), "******** can not go to hub home activity ********"
        # self.device(description="Open navigation drawer").click()
        # self.device.wait.idle()

        if self.is_account_login(account):
            return True

        assert self.device(description="Add account").wait.exists(), "******** can not find add account menu ********"
        self.device(description="Add account").click()
        self.device.wait.idle()

        assert self.device(text="Email address").wait.exists(), "******** can not input email address  ********"
        self.device(text="Email address").set_text(account)
        self.device.delay(2)

        self.device(text="NEXT").click()
        self.device.wait.idle()
        self.device.delay(2)

        # following steps maybe different for enterprise account or personal account login
        if "enterprise" in account_type:
            self._login_with_enterprise(account, pwd)
        elif "personal" in account_type:
            self._login_with_personal(account, pwd)
        return True

    def _login_with_enterprise(self, account, pwd):
        """
            steps for login enterprise account
        """
        self.logger.info("try to login with enterprise account")
        assert self.device(text="Password").wait.exists(timeout=2 * 60 * 1000), "******** can not input pwd  ********"
        self.device(text="Password").set_text(pwd)
        self.device.wait.idle()
        self.device.delay(2)

        self.device(text="NEXT").click()
        self.device.wait.idle()

        if self.device(text="MICROSOFT EXCHANGE ACTIVESYNC").wait.exists():
            self.device(text="MICROSOFT EXCHANGE ACTIVESYNC").click.wait()
            self.device.wait.idle()
            self.logger.debug("device is idle")
            self.device(text="CANCEL").wait.gone(timeout=60 * 1000)
            self.device.wait.idle()
            if "tcl.com" in account:
                self.device(scrollable=True).scroll.vert.toEnd()
                assert self.device(resourceId="com.blackberry.infrastructure:id/account_server").ext5
                self.device(resourceId="com.blackberry.infrastructure:id/account_server").set_text("mail.tcl.com")

            if self.device(text="NEXT").ext5:
                self.device(text="NEXT").click.wait()

        if self.device(text="Remote security administration").wait.exists(timeout=15 * 60 * 1000):
            self.device(resourceId="android:id/button1").click()
            self.device.wait.idle()

        assert self.device(
            text="NEXT").wait.exists(), "******** can not find next btn in account options activity  ********"
        self.device(text="NEXT").click()
        self.device.wait.idle()

        if self.device(text="Security update").wait.exists(timeout=15 * 60 * 1000):
            self.device(resourceId="android:id/button1").click()
            self.device.wait.idle()

        for i in range(90):
            if self.device(text="Activate device admin app?").exists or self.device(
                    text="Activate device administrator?").exists:
                break
            self.device.delay(10)

        # if self.device(text="Activate device admin app?").wait.exists(timeout=15 * 60 * 1000):
        self.device.swipe(500, 1600, 500, 300)
        assert self.device(
            resourceId="com.android.settings:id/action_button").wait.exists(), "****** can not find Activate this device administrator btn *****"
        self.device(resourceId="com.android.settings:id/action_button").click()
        self.device.wait.idle()

        assert self.device(text="DONE").wait.exists(timeout=3000)
        self.device(text="DONE").click()
        self.device(text="DONE").wait.gone()

        if self.device(text="Add to home screen?").wait.exists(timeout=3000):
            self.device(text="CANCEL").click.wait()

        assert self.is_hub_home(), "****** do not go to hub home after the account login ******"
        return True

    def _login_with_personal(self, account, pwd):
        """
            steps for login enterprise account
            @param pwd:
            @return:
        """
        self.logger.info("try to login with personal account")
        if self.device(text="Next").exists:
            self.device(text="Next").click()
        elif self.device(resourceId="next").wait.exists(timeout=30000):
            self.device(resourceId="next").click()
        else:
            assert False, "can not found next button"
        self.device.wait.idle()

        assert self.device(resourceId="email-display").wait.exists(timeout=30000)
        text = self.device(resourceId="email-display").get_text()
        assert text == account, "******** can not turn to Google account login setupwizard  ********"
        self.device.delay(2)
        assert self.device(resourceId="Passwd").wait.exists(
            timeout=2 * 60 * 1000), "******** can not input pwd  ********"
        self.device(resourceId="Passwd").set_text(pwd)

        self.device.delay(2)
        assert self.device(resourceId="signIn").wait.exists(
            timeout=2 * 60 * 1000), "******** can not Sign in btn  ********"
        self.device(resourceId="signIn").click()
        self.device.wait.idle()

        assert self.device(resourceId="submit_approve_access").wait.exists(
            timeout=15 * 60 * 1000), "******** can not find allow btn in 'BlackBerry would like to' activity  ********"
        # click allow until it is gone
        # self.device(scrollable=True).scroll.vert.toEnd(steps=10)
        if self.device(resourceId="submit_approve_access").exists:
            self.device.delay(10)
            self.device(resourceId="submit_approve_access").click()
            self.device(resourceId="submit_approve_access").wait.gone(timeout=2000)

        assert self.device(text="Account options").wait.exists(
            timeout=15 * 60 * 1000), "******** can not find account options activity  ********"
        self.device(text="NEXT").click()
        self.device.wait.idle()

        assert self.device(text="DONE").wait.exists(timeout=15 * 60 * 1000)
        self.device(text="DONE").click()
        self.device(text="DONE").wait.gone()

        if self.device(text="Add to home screen?").wait.exists(timeout=3000):
            self.device(text="CANCEL").click.wait()

        assert self.is_hub_home(), "***** do not go to hub home after the account login *****"
        return True

    def send_mail_with_pic_via_given_account(self, from_account, to_account, subject):
        """
        sent email with a pic to the given account,
        the pic is capture from camera
        @param from_account: account who sent the mail
        @param to_account: account who receive the mail
        @param subject: subject of the mail
        @return: true if email sent out, but do not verify sent successfully or not
        """
        assert self.is_account_login(from_account)
        self.device(text=from_account).click()

        assert self.device(
            resourceId="com.blackberry.hub:id/signature_fab").wait.exists(), "can not find btn to create email"
        self.device(resourceId="com.blackberry.hub:id/signature_fab").click()
        self.device.wait.idle()

        assert self.device(text="Compose").wait.exists(timeout=3000), "email compose activity do not launched"
        # set to
        self.device(resourceId="com.blackberry.hub:id/tagTextViewContainer").child(index=0).set_text(to_account)

        # attach pic
        self.device(resourceId="com.blackberry.hub:id/attach").click()
        self.device.wait.idle()
        assert self.device(text="Take a photo").wait.exists(timeout=3000), "can not find 'Take a photo' menu"
        self.device(text="Take a photo").click()
        self.device.wait.idle()

        assert self.device(resourceId="com.blackberry.camera:id/capture_button_timer_progress").wait.exists(
            timeout=10000), "can not find capture btn"
        self.device(resourceId="com.blackberry.camera:id/capture_button_timer_progress").click()
        self.device.wait.idle()

        # get pic name
        pic_name = self.device(resourceId="com.blackberry.hub:id/attachment_name").get_text()
        # set subject
        self.device(resourceId="com.blackberry.hub:id/subjectField").set_text(subject + '_' + pic_name)
        # set body
        # self.device(descriptionContains="Sent from my BlackBerry").click.topleft()
        # self.device(descriptionContains="Sent from my BlackBerry").set_text(body)

        # send
        self.device(resourceId="com.blackberry.hub:id/send").click()
        self.device.wait.idle()

        assert self.device(
            resourceId="com.blackberry.hub:id/smallButton").wait.exists(), "******** can not find image size selection  ********"
        self.device(resourceId="com.blackberry.hub:id/smallButton").click()
        self.device.wait.idle()

        self.device(text="SEND").click()
        self.device.wait.idle()

        # assert email sent, but do not verify sent successfully or not
        assert self.device(textContains=subject).wait.exists(timeout=3000)
        return True

    def verify_received_mail_with_pic(self, subject):
        """
        verify mail which with pic in it
        @param subject:
        @return: true if the pic received can be opened
        """
        attachment_name_prefix = "Camera_IMG"
        assert self.is_hub_home(), "hub do not opened successfully"

        self.open_mail_via_search_with_subject(subject)

        # assert email details opened
        assert self.device(description="More options").wait.exists(), "******** can not open email details  ********"
        # verify attachment name is correct or not, this step is not necessary
        assert self.device(
            resourceId="com.blackberry.hub:id/attachment_name").wait.exists(), "******** have no attachment ********"
        attachment_name = self.device(resourceId="com.blackberry.hub:id/attachment_name").get_text()
        assert attachment_name_prefix in attachment_name, "attachment is not a pic came from camera"

        # open attachment, and verify can it be opened or not
        self.device(resourceId="com.blackberry.hub:id/attachment_name").click()
        self.device.wait.idle()
        assert self.device(resourceId="com.google.android.apps.photos:id/details").wait.exists(
            timeout=10 * 1000), "******** attachment can not be opened  ********"

        return True

    def send_mail_with_keywords(self, from_account, to_account, subject, body, body_repeat_loops=0,
                                long_msg_end="LONG_MSG_INPUT_DONE"):
        """
        send mail or a long mail
        @param from_account:
        @param to_account:
        @param subject:
        @param body: content for email body, it MUST be a short string WITHOUT ANY space, otherwise the string can ont be input.
        @param body_repeat_loops: 0, no repeat, >0, repeat the given loops to generate a long mail, default is 0, means a short mail
        @param long_msg_end: end flag, this is helpful to verify the long mail
        @return: true if mail sent out, but do not verify mail is delivered successfully or not
        """
        self.logger.info("try to send mail")
        assert self._select_account(from_account), "****** can not select account %s *******" % from_account

        assert self.device(
            resourceId="com.blackberry.hub:id/signature_fab").wait.exists(), "can not find btn to create email"
        self.device(resourceId="com.blackberry.hub:id/signature_fab").click()
        self.device.wait.idle()

        assert self.device(text="Compose").wait.exists(timeout=3000), "email compose activity do not launched"
        # set to
        self.device(resourceId="com.blackberry.hub:id/tagTextViewContainer").child(index=0).set_text(to_account)

        # set subject
        self.device(resourceId="com.blackberry.hub:id/subjectField").set_text(subject)

        # set body
        self.device(resourceId="com.blackberry.hub:id/body_fragment").click.topleft()  # set focus
        self.device.wait.idle()
        if body_repeat_loops:  # if it is for long msg test
            # if no del, it fail to input the first  character of body
            self.adb.shell("input keyevent KEYCODE_DEL")
            for i in range(body_repeat_loops):
                self.adb.shell("input text %s" % body)
                self.adb.shell("input keyevent KEYCODE_ENTER")
            else:
                self.adb.shell("input keyevent KEYCODE_ENTER")
                self.adb.shell("input text %s" % long_msg_end)
        else:
            self.adb.shell("input keyevent KEYCODE_DEL")
            self.adb.shell("input text %s" % body)
        self.device.delay()

        # send
        self.device(resourceId="com.blackberry.hub:id/send").click()
        self.device.wait.idle()

        # assert email sent, but do not verify mail is delivered successfully or not
        assert self.device(textContains=subject).wait.exists(timeout=3000)
        return True

    def process_mail_with_keywords(self, subject, action="file"):
        """
        process the mail, del or file
        @param subject: help to find the mail to process
        @param action: the accept actions: file or del. default is file
        @return:
        """
        self.logger.info("process mail, action %s" % action)
        self.open_mail_via_search_with_subject(subject)

        # play action accordingly
        if "del" in action:
            self._perform_action_del()
            assert not self.device(resourceId="com.blackberry.hub:id/text_2",
                                   textContains=subject).wait.exists(), "******** mail do not del  ********"
        elif "file" in action:
            self._perform_action_file()
            assert self.back_to_hub_home(), "mail do not filed, do not back to hub home"
        else:
            self.logger.error("incorrect action, only 'del' and 'file' implemented ")
            return False

        return True

    def open_mail_via_search_with_subject(self, subject):
        """
        open mail with given subject from search menu,
        @param subject:
        @return:
        """
        self.logger.info("search mail with subject '%s'" % subject)
        assert self.is_hub_home(), "hub do not opened successfully"
        # open search btn
        assert self.device(
            resourceId="com.blackberry.hub:id/search_menu_item").wait.exists(), "******** can not find search btn ********"
        self.device(resourceId="com.blackberry.hub:id/search_menu_item").click()
        self.device.wait.idle()
        # input text as given subject
        assert self.device(
            resourceId="android:id/search_src_text").wait.exists(), "******** can not find search textbox   ********"
        self.device(resourceId="android:id/search_src_text").set_text(subject)
        self.device.wait.idle()
        # get search result, and click email

        #####并不是每一次都会找第一行，这个判断有时候并不可靠
        # assert self.device(resourceId="com.blackberry.hub:id/text_2",
        #                    textContains=subject).wait.exists(
        #     timeout=30000), "******** can not find result match the given subject, email sent fail ********"

        search_result_element = self.device(resourceId="com.blackberry.hub:id/swipe_layout", index=1).child(
            resourceId="com.blackberry.hub:id/list_item_background").child(
            resourceId="com.blackberry.hub:id/text_container").child(
            resourceId="com.blackberry.hub:id/text2_container").child(resourceId="com.blackberry.hub:id/text_2",
                                                                      textContains=subject)
        if search_result_element.wait.exists(timeout=30000):
            self.logger.debug("verifier subject '%s' successfully" % subject)
        else:
            raise ValueError(
                "******** can not find result match the given subject '%s', email sent fail ********" % subject)

        search_result_element.click()
        self.device.wait.idle()

        self.device.delay(3)
        if not (self.device(description="Delete message").wait.exists() or self.device(description="Delete").exists):
            self.device(resourceId="com.blackberry.hub:id/text_2", textContains=subject).click()
            self.device.wait.idle()

        assert (self.device(description="Delete message").wait.exists() or self.device(description="Delete").exists), \
            "******** can not find more option, email do not opened   ********"
        self.device.delay()

        if not self.device(
                resourceId="com.blackberry.calendar:id/view_event_fragment_response_bar_accept_button").exists:
            self.device.press.back()
            self.device.delay()
            self.device(resourceId="com.blackberry.hub:id/text_2", textContains=subject).click.wait()

    def _perform_action_del(self):
        """
        steps for del mail
        @return:
        """
        self.logger.debug("starting to delete the mail")
        assert self.device(description="Delete").wait.exists(), "******** can not find delete btn  ********"
        self.device(description="Delete").click()
        self.device.wait.idle()

        assert self.device(resourceId="android:id/button1",
                           text="DELETE").wait.exists(), "******** can not find 'Delete?'  ********"
        self.device(resourceId="android:id/button1").click()
        self.device.wait.idle()

    def _perform_action_file(self):
        """
        steps for file mail
        @return:
        """
        assert self.device(description="File").wait.exists(), "******** can not find file btn  ********"
        self.device(description="File").click()
        self.device.wait.idle()

        assert self.device(text="Inbox").wait.exists(), "******** can not find inbox btn  ********"
        self.device(text="Inbox").click()
        self.device.wait.idle()

    def _select_account(self, account):
        """
        select the given account from menu setting, the menu setting MUST be opened
        @param account:
        @return:
        """
        self.logger.debug("try to select account %s" % account)
        if self.device(text=account).wait.exists():
            return True

        assert self.is_account_login(account)
        self.device(text=account).click()
        self.device.wait.idle()
        assert self.device(text=account).wait.exists()
        self.logger.debug("select account %s successfully" % account)
        return True

    def verify_mail(self, subject, long_msg_end="LONG_MSG_INPUT_DONE"):
        """
        verify received mail or long mail
        @param subject:
        @param long_msg_end: the flag for the ending of long mail, default value is same as send_mail_with_keywords
        @return:
        """
        self.logger.info("verify mail")
        self.open_mail_via_search_with_subject(subject)
        if not long_msg_end:
            return True

        # self.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)
        self.device.swipe(550, 1150, 550, 350)
        assert self.device(description=long_msg_end).wait.exists() or self.device(
            text=long_msg_end).wait.exists(), "******** can not find flag for long_msg_end = %s  ********" % long_msg_end
        return True

    def reply_mail(self, subject, reply_action="", is_reply_1_time=True, forward_to=""):
        """
        reply mail when email is opened, multi method reply or forward email,
        if mail is long, scroll to the end, the reply icon will be only one,
        this method has logic for this situation
        @param subject:
        @param reply_action: the action MUST be 'reply_all' or 'reply' or 'forward' or 'forward_with_text'
        @param is_reply_1_time: discarded, do not use it current now. if the mail was reply more than 1 times, the action btn changed,
        @param forward_to: account to forward
        @return:
        """
        # self.logger.debug("******* reply_action=%s ******" % reply_action)
        self.logger.info("perform reply, action is %s" % reply_action)

        if self.device(resourceId="com.blackberry.hub:id/icons_bar_instance").wait.exists(timeout=3000):
            if "reply" == reply_action:
                action_btn = self.device(
                    resourceId="com.blackberry.hub:id/fab_toolbar_icon_0") if is_reply_1_time else self.device(
                    resourceId="com.blackberry.hub:id/action_reply")
            elif "reply_all" == reply_action:
                action_btn = self.device(
                    resourceId="com.blackberry.hub:id/fab_toolbar_icon_1") if is_reply_1_time else self.device(
                    resourceId="com.blackberry.hub:id/action_reply_all")
            elif "forward" in reply_action:
                action_btn = self.device(
                    resourceId="com.blackberry.hub:id/fab_toolbar_icon_2") if is_reply_1_time else self.device(
                    resourceId="com.blackberry.hub:id/action_forward")
            else:
                self.logger.error(
                    "******* have no action you input, only reply_all, reply, forward are implemented ******")
                return False

            assert action_btn.wait.exists(), "******** can not find action btn  ********"
            action_btn.click()
            self.device.wait.idle()

            if "forward" == reply_action:
                self._perform_fw_action(forward_to, forward_text="")
            elif "forward_with_text" == reply_action:
                self._perform_fw_action(forward_to)

            self._click_send()

            return True
        elif self.device(resourceId="com.blackberry.hub:id/circle_instance").wait.exists():
            self.logger.info("circle icon found")
            self.device(resourceId="com.blackberry.hub:id/circle_instance").click()
            self.device.wait.idle()
            self._click_send()
            assert self.device(textContains="Re: " + subject).wait.exists(timeout=3000)
            return True

        else:
            self.logger.error("******* can not find any reply or forward btn ******")
            return False

    def _click_send(self):
        """
        click send btn
        @return:
        """
        assert self.device(
            resourceId="com.blackberry.hub:id/send").wait.exists(), "******** can not find send btn  ********"
        self.device(resourceId="com.blackberry.hub:id/send").click()
        self.device.wait.idle()

    def _perform_fw_action(self, forward_to, forward_text="forward_test"):
        """
        perform forward action, just forward or forward with text
        @param forward_to:
        @param forward_text: a flag for forward text, default is forward_test
        @return:
        """
        self.logger.info("perform forward action")
        assert forward_to, "****** pls give one email for forward ******"
        self.adb.shell("input keyevent KEYCODE_DEL")
        self.device.wait("idle")
        self.device(className="android.widget.MultiAutoCompleteTextView").set_text(forward_to)
        self.device.wait("idle")
        self.adb.shell("input keyevent KEYCODE_ENTER")

        if forward_text:
            assert self.device(
                resourceId="com.blackberry.hub:id/body_fragment").wait.exists(), "******** can not find body  ********"
            self.device(resourceId="com.blackberry.hub:id/body_fragment").click.topleft()
            self.device.wait.idle()
            self.adb.shell("input text %s" % forward_text)

    def verify_mail_group(self, subject):
        """
        verify a group mail list
        @param subject:
        @return:
        """
        self.logger.info("verify a group mail list")
        assert self.device(
            textContains="Fw: " + subject).wait.exists(), "******** can not find email forward by m device ********"
        self.device(textContains="Fw: " + subject).click()
        self.device.wait.idle()

        self.device.delay()  # wait for email opened

        assert self.device(
            resourceId="com.blackberry.hub:id/conversation_unread_count").wait.exists(), "******** can not find unread count btn  ********"
        received_email_num = self.device(resourceId="com.blackberry.hub:id/conversation_unread_count").get_text()
        for i in range(5):
            if int(received_email_num) == 3:
                break
            self.device.delay(5)
            received_email_num = self.device(resourceId="com.blackberry.hub:id/conversation_unread_count").get_text()

        assert int(
            received_email_num) == 3, "******** should got 4 email, but got %s email in first container  ********" % received_email_num
        # self.device.swipe(300, 1400, 300, 300)
        while self.device(resourceId="com.blackberry.hub:id/email_snippet",
                          textContains="Sent from my BlackBerry").wait.exists():
            self.device(resourceId="com.blackberry.hub:id/email_snippet").click()
            self.device.delay(1)  # wait for email opened
            self.device.swipe(300, 1400, 300, 300)  # go to next msg
        else:
            self.logger.debug(
                "******* read all mail, go back to beginning and verify unread count icon, it should be none ******")
        self.device.swipe(300, 300, 300, 1400)
        assert not self.device(
            resourceId="com.blackberry.hub:id/conversation_unread_count").wait.exists(), "******** unread count icon still exist, verify your step  ********"
        return True

    def del_all_mails(self, items="", del_num=20):
        """
        del all item one by one in hub,
        @param del_num: default is 0, means del all item, >0, means del item from beginning to the given num
        @return:
        """
        try:
            self.logger.debug("starting to delete the sent items emails %d times" % del_num)
            if not self.is_hub_home():
                self.enter()
            if items:
                self.enter_box(items)
            # assert self.is_hub_home(), "***** can not open hub home *****"
            if not del_num:  # del all mails
                while self._perform_del_gesture():
                    pass
            else:
                for i in xrange(del_num):
                    self.logger.debug("delete email %d times" % i)
                    if not self._perform_del_gesture():
                        self.logger.debug("can not found emails,maybe all of emails are deleted")
                        break
        except:
            self.logger.warning(traceback.format_exc())
        self.logger.debug("delete the sent items emails %d times completed" % del_num)

    def _perform_del_gesture(self):
        """
        del item in hub via swipe gesture, if any exception found, just ignore,
        @return:
        """
        try:
            assert self.device(
                resourceId="com.blackberry.hub:id/swipe_layout").wait.exists(), "******** can not find item to del  ********"
            x, y = self.device(resourceId="com.blackberry.hub:id/swipe_layout").get_location()
            # print x, ",", y
            self.device.swipe(x, y, 10, y, steps=20)

            assert self.device(resourceId="android:id/button1").wait.exists(
                timeout=3000), "******** can not find confirm DELETE btn after perform del gesture ********"
            self.device(resourceId="android:id/button1").click()
            self.device.delay()
            return True
        except:
            self.logger.debug("******* del mail failed, but this operation do not effect test result ******")
            return False


if __name__ == '__main__':
    a = Email("80c08ac6", "Email")
    # a.enter()
    # a.send_mail("Reply", True, "jia.huang@tcl.com")
    # a.del_mail("Sent")
    # a.del_mail('Trash')
    # a.enter_box("Inbox")
    # a.create_draft("jia.huang@tcl.com", 1)
    # a.send_draft(1)
    # a.del_mail('Sent')
    # a.del_mail('Trash')
    # a.enter_box("Inbox")
