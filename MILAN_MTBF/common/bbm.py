#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: bbm.py
@time: 2017/9/1 19:23

script about BBM
"""

from common import *


class BBM(Common):
    def enter_new(self):
        """Launch BBM by StartActivity.
        """
        self.logger.debug('enter BBM and check to see if it is logged in')
        if self.device(text="Welcome to BBM").wait.exists(timeout=5 * 1000) \
                or self.device(resourceId="formId:signinPhone").ext5 \
                or self.device(resourceId="formId:signUpWithPhone").ext5:
            self.logger.debug('BBM(without login)  is already open')
            return True
        self.start_app("BBM")
        self.device.wait.idle()
        time.sleep(5)
        # dumpinfo = self.device.dump()
        # print dumpinfo
        if self.device(text="Welcome to BBM").wait.exists(timeout=30 * 1000) \
                or self.device(resourceId="formId:signinPhone").ext5 \
                or self.device(resourceId="formId:signUpWithPhone").ext5:
            self.logger.debug('Enter BBM(without login) successfully')
            return True
        else:
            self.logger.debug('******** Enter BBM(without login) failed ********')
            return False

    def enter(self):
        self.logger.debug('enter BBM')
        if self.is_signed():
            self.logger.debug('BBM started with account sign in')
            return True
        self.start_app("BBM")

        if self.device(text="There are Contacts and then there are BBM Contacts.").wait.exists():
            self.device(text="There are Contacts and then there are BBM Contacts.").click()
            self.device.wait("idle")

        while self.device(resourceId="com.android.packageinstaller:id/permission_allow_button").wait.exists():
            self.device(resourceId="com.android.packageinstaller:id/permission_allow_button").click.wait()
        for i in range(10):
            if self.device(description="Welcome to BBM").exists or self.device \
                        (resourceId="com.bbm:id/floatingButton").exists or self.device(description="Sign In").exists:
                break
            if self.device(text="CONTINUE").exists:
                self.device(text="CONTINUE").click.wait()
            self.device.delay(2)
        self.device.wait("idle")
        if self.is_signed():
            self.logger.debug('BBM started with account sign in')
            return True
        elif self.device(text="SIGN IN").wait.exists(timeout=30 * 1000):
            self.logger.debug('BBM started with none account sign in')
            return True

        else:
            self.logger.debug('BBM started failed')
            return False

    def delete_contacts(self, contact_name):
        self.logger.debug("try to delete contacts " + contact_name)
        self.go_to_tab("Contacts")
        if self.device(text=contact_name).wait.exists():
            self.device(text=contact_name).long_click()
            self.device.wait("idle")
            assert self.device(description="More options").wait.exists(timeout=1000), "Can't find more options item"
            self.device(description="More options").click.wait()
            if self.device(text="Delete").exists:
                self.device(text="Delete").click.wait()
            self.device(text="DELETE").click.wait()
            return not self.device(text=contact_name).exists
        else:
            return True

    def is_signed_new(self):
        if self.device(resourceId="com.bbm:id/bottom_navigation_item_container").wait.exists():
            self.logger.debug('BBM was singed')
            return True
        else:
            self.logger.debug('******** BBM was not singed ********')
            self.save_fail_img()
            return False

    def is_signed(self):
        if self.device(resourceId="com.bbm:id/menu_chats").ext5:
            self.logger.debug('BBM was singed')
            return True
        if self.device(text="There are Contacts and then there are BBM Contacts.").wait.exists(timeout=10000):
            self.device(text="There are Contacts and then there are BBM Contacts.").click()
            self.device.wait("idle")
        if self.device(resourceId="com.bbm:id/menu_chats").ext5:
            self.logger.debug('BBM was singed')
            return True
        else:
            self.logger.debug('******** can not found resourceid "com.bbm:id/menu_chats",BBM was not singed ********')
            # self.save_fail_img()
            return False

    def login_with_email(self, email_account, email_pwd):
        self.logger.debug('Try to sign in BBM with email account')
        if self.device(resourceId="formId:signinPhone").wait.exists(timeout=15000):
            self.device(resourceId="formId:signinPhone").click()
        elif self.device(text="SIGN IN").ext5:
            self.device(text="SIGN IN").click()
        elif self.device(text="Sign In").ext5:
            self.device(text="Sign In").click()
        else:
            self.logger.warning("Can not found 'SIGN IN',try to click point 286,1521")
            self.device.click(286, 1521)
        self.device.wait("idle")
        # if self.device(resourceId="formId:signinEmail").wait.exists(timeout=10000):
        #     self.device(resourceId="formId:signinEmail").click()
        #     self.device.wait("idle")
        # if self.device(text = "Email Address").wait.exists(timeout=10000):
        #     self.logger.debug("click Email Address")
        #     self.device(text = "Email Address").click()
        #     self.device(text = "Email Address").set_text(email_account)
        #     self.device.press.enter()
        if self.device(resourceId="formId:email").wait.exists(timeout=15000):
            self.logger.debug("click formId:email")
            self.device(resourceId="formId:email").click()
            self.device(resourceId="formId:email").set_text(email_account)
            self.device(resourceId="formId:email").click()
        elif self.device(resourceId="usernameSection").wait.exists(timeout=15000):
            self.logger.debug("click usernameSection")
            self.device(resourceId="usernameSection").click()
            self.device(resourceId="usernameSection").set_text(email_account)
            self.device(resourceId="usernameSection").click()
        else:
            self.logger.debug("can not found Email Address")

        if self.device(text="AUTOFILL").wait.exists(timeout=15000):
            self.logger.debug("cancel autofill")
            self.device(text="CANCEL").click.wait()
        else:
            self.logger.debug("not found autofill")

        if self.device(resourceId="formId:password").ext5:
            self.logger.debug("found 'formId:password'")
            self.device(resourceId="formId:password").click()
            self.device(resourceId="formId:password").set_text(email_pwd)
        self.device.wait("idle")

        # if self.device(text="Show").exists:
        #     self.device(text="Show").click.wait()
        # assert self.device(text=email_account).wait.exists(), "email account do not input successfully, can not sign in"
        # assert self.device(text=email_pwd).wait.exists(), "email pwd do not input successfully, can not sign in"

        if self.device(resourceId="formId:logincommandLink").ext5:
            self.device(resourceId="formId:logincommandLink").click()
            self.device.wait("idle")

        if self.device(text="CONTINUE").wait.exists(timeout=5 * 1000):
            self.device(text="CONTINUE").click.wait()

        if self.device(text="Find Friends").wait.exists(timeout=30 * 1000):
            self.logger.debug("Find Friends")
            self.device(resourceId="android:id/button1").click()
            self.device.wait("idle")

        if self.device(resourceId="com.bbm:id/button_continue").wait.exists(timeout=5 * 1000):
            self.device(resourceId="com.bbm:id/button_continue").click()
            self.device.wait("idle")

        if self.device(text="No Thanks").wait.exists(timeout=5 * 1000):
            self.device(text="No Thanks").click()
            self.device.wait("idle")

        if self.device(text="ALLOW").wait.exists(timeout=5 * 1000):
            self.device(text="ALLOW").click.wait()

        if self.device(text="ALLOW").wait.exists(timeout=5 * 1000):
            self.device(text="ALLOW").click.wait()

        if self.device(text="com.bbm:id/floating_action_button").ext5:
            self.logger.debug("sign in bbm successfully")

        if self.device(resourceId="com.bbm:id/menu_contacts").ext5:
            self.device(resourceId="com.bbm:id/menu_contacts").click()
            self.logger.debug("click 151,1385")
            time.sleep(3)
            self.device.click(151, 1385)
            time.sleep(3)

        if self.device(text="There are Contacts and then there are BBM Contacts.").wait.exists(timeout=30 * 1000):
            self.device(text="There are Contacts and then there are BBM Contacts.").click()
            self.device.wait("idle")

            if self.device(text="com.bbm:id/floating_action_button").ext5:
                self.logger.debug("dismiss popup 'There are Contacts and then there are BBM Contacts.' successfully")
        return True

    def go_to_tab(self, tab_desc):
        """go to tab you wanted
        :param tab_desc: description of the tab
        """
        self.logger.debug('try to go to tab %s' % tab_desc)
        self.enter()
        if self.device(description=tab_desc).wait.exists(timeout=5000):
            self.device(description=tab_desc).click()
            self.logger.debug("go to tab %s successfully" % tab_desc)
            return True
        else:
            self.logger.debug('******** can not find tab %s  ********' % tab_desc)
            return False

    def add_new_contact(self, pin_s):
        self.logger.debug('try to add new contact')
        self.go_to_tab("Contacts")

        assert self.device(resourceId="com.bbm:id/floatingButton", description="Add Contact").wait.exists(timeout=5000), \
            "******** can not find btn for adding account ********"
        self.device(resourceId="com.bbm:id/floatingButton").click()

        if self.device(text="Add by PIN").wait.exists():
            self.device(text="Add by PIN").click()
            self.device.wait("idle")

        assert self.device(resourceId="com.bbm:id/invite_pin").wait.exists(timeout=3000), "pin code do not display"
        self.device(resourceId="com.bbm:id/invite_pin").set_text(pin_s)

        assert self.device(resourceId="com.bbm:id/invite_pin_suggestion").wait.exists(timeout=3000)
        self.device(resourceId="com.bbm:id/invite_pin_suggestion").click()

        self.device(resourceId="com.bbm:id/toolbar_done_button").click()
        # assert self.is_signed()
        return True

    def agree_invitation(self, user_name):
        self.logger.debug('try to agree invitation')
        # if not self.is_signed():
        #     return False
        self.go_to_tab("Chats")

        assert self.device(resourceId="com.bbm:id/invites_item").wait.exists(
            timeout=5000), "******** can not find any invites ****"
        self.device(resourceId="com.bbm:id/invites_item").click()
        self.device.wait.idle()

        assert self.device(resourceId="com.bbm:id/contact_name").wait.exists(
            timeout=5000), "******** can not find invite ****"
        self.device(resourceId="com.bbm:id/contact_name").click()
        self.device.wait.idle()

        assert self.device(
            resourceId="com.bbm:id/accept_pending_invite").wait.exists(
            timeout=5000), "******** can not find accept ****"
        self.device(resourceId="com.bbm:id/accept_pending_invite").click()
        self.device.wait.idle()

        self.back_to_bbm_home()
        self.go_to_tab("Contacts")

        assert self.device(text=user_name).wait.exists(
            timeout=6000), "******** contact add failed, ckeck your steps ****"
        return True

    def del_contact(self, user_name):
        self.logger.debug('try to del new contact')
        # if not self.is_signed():
        #     return False
        self.go_to_tab("BBM Contacts")
        if self.device(text=user_name).wait.exists(timeout=3000):
            self.device(text=user_name).long_click()
            self.device.wait.idle()
        else:
            self.logger.debug('can not find contact %s' % user_name)

        assert self.device(description="More options").wait.exists(), "******** can not find more option ********"
        self.device(description="More options").click()
        self.device.wait.idle()

        assert self.device(text="Delete").wait.exists(), "******** can not find del btn *********"
        self.device(description="More options").click()
        self.device.wait.idle()

        assert self.device(text="DELETE").wait.exists(), "******** can not find delete confirm alarm ********"
        self.device(text="DELETE").click()
        self.device.wait.idle()

        assert not self.device(text=user_name).wait.exists(), "******** %s do del failed ********" % user_name
        return True

    def get_pin(self):
        assert self.go_to_account_info(), "can not open account infor page"
        bbm_pin = self.device(resourceId="com.bbm:id/pin").get_text()
        assert bbm_pin.isalnum(), "the pin code is incorrect"
        assert self.back_to_bbm_home(), "do not back to BBM home after get account infor"
        return bbm_pin

    def get_username(self):
        self.logger.debug("starting to get username")
        assert self.go_to_account_info(), "can not open account infor page"
        bbm_username = self.device(resourceId="com.bbm:id/user_name").get_text()
        assert self.back_to_bbm_home(), "do not back to BBM home after get account infor"
        return bbm_username

    def go_to_account_info(self):
        # if not self.is_signed():
        #     return False
        self.go_to_tab("Me")
        assert self.device(resourceId="com.bbm:id/user_layout").ext5, "******** go to tab me failed ********"
        return True

    def sent_msg(self, user_name_m, msg):
        self.logger.debug("sent msg:%s" % msg)
        self.enter()
        self.go_to_tab("Contacts")
        assert self.device(text=user_name_m).wait.exists(timeout=3000), "******** can ont find user name ********"
        self.device(text=user_name_m).click()
        self.device.wait.idle()

        if self.device(resourceId="com.bbm:id/tech_tip_title").wait.exists():
            self.device(resourceId="com.bbm:id/tech_tip_title").click()
            self.device.wait.idle()

        assert self.device(
            resourceId="com.bbm:id/message_input_text").wait.exists(), "****** conversation page do not started *******"
        self.device(resourceId="com.bbm:id/message_input_text").set_text(msg)
        self.device.wait.idle()

        assert self.device(
            resourceId="com.bbm:id/send_button").wait.exists(), "******** can not find sent btn  ********"
        self.device(resourceId="com.bbm:id/send_button").click()
        self.device.wait.idle()

        assert self.device(resourceId="com.bbm:id/message_body",
                           text=msg).wait.exists(), "******** message may not send out  ********"
        # self.device.press.back()
        # self.device.press.back()

        assert self.back_to_bbm_home(), "can not back to BBM home after sent a msg"
        return True

    def verify_msg_received(self, msg, timeout=5):
        self.logger.debug("verify msg received %s seconds" % timeout)
        self.device.delay(timeout)
        self.go_to_tab("Chats")
        assert self.device(resourceId="com.bbm:id/message",
                           text=msg).wait.exists, "******** do not receive msg after %ss  ********" % timeout
        return True

    def back_to_bbm_home(self):
        self.logger.debug('back to BBM home')
        for i in range(5):
            if self.device(resourceId="com.bbm:id/bottom_navigation_item_container").wait.exists():
                return True
            else:
                self.logger.debug("press back")
                self.device.press.back()
        else:
            self.logger.debug('can not back to bbm home')
            return False


if __name__ == '__main__':
    a = BBM("2cd0e633", "Music")
    print a.device.dump(r"c:\recorder.xml")
