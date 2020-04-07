# -*- coding: UTF-8 -*-
"""Telephony library for scripts.
"""
import re

from common import *
from native_music import native_Music


class Telephony(Common):
    package = 'com.tct.dialer'
    launch_activity = 'com.android.dialer.app.DialtactsActivity'

    def __init__(self, device, log_name, sdevice=None):
        Common.__init__(self, device, log_name, sdevice)
        self.music = native_Music(self.device, "tel_music")
        self.float_btn = self.device(
            resourceId='com.google.android.contacts:id/floating_action_button',
            description="Create contact")  # contacts home marking
        self.float_btn_contacts = self.device(resourceId='com.tct.contacts:id/floating_action_button')  # contacts home marking
        self.call_protection = self.device(text="Call protection")  # phone setup wizard marking
        self.key_pad = self.device(resourceId="com.google.android.dialer:id/fab")
        self.call_btn = self.device(resourceId="com.google.android.dialer:id/dialpad_floating_action_button")
        self.end_call_btn = self.device(resourceId="com.google.android.dialer:id/incall_end_call")

    # def enter_phone(self):
    #     if self.is_phone_homepage():
    #         return True
    #     self.logger.info('start phone')
    #     self.start_app('Phone')
    #     return self.is_phone_homepage()

    def is_phone_homepage(self):
        if self.device(description="key pad").exists:
            self.logger.info('Has entered the phone homepage')
            return True
        else:
            self.logger.info('Not in phone homepage')
            return False

    def enter_dialer(self):
        self.logger.debug("Enter Dialer")
        if self.is_phone_homepage():
            return True
        self.start_app('Phone')
        return self.is_phone_homepage()

    def is_contacts_home(self):
        if self.float_btn.exists:
            self.logger.info('Has entered the contacts homepage')
            return True
        else:
            self.logger.info('Not in contacts homepage')
            return False

    def enter_contacts(self):
        self.logger.debug("Launch Contacts")
        if self.is_contacts_home():
            self.logger.debug("The contacts homepage has been entered")
            return True
        self.start_app('Contacts')
        # verify contacts home exists
        return self.is_contacts_home()

    def back_to_contact(self):
        """back to contacts list.
        """
        self.logger.debug("start to back to contact list page")
        for loop in range(5):
            if self.float_btn.wait.exists(timeout=1000):
                self.logger.debug("back to contact list page successfully")
                return True
            self.device.press.back()
        self.logger.debug("back to contact list page failed")
        return False

    def dialer_secret_code(self, code_number):
        self.enter_dialer()

        # click OK to exist secured code input
        if self.device(resourceId="android:id/button1").exists:
            self.device(resourceId="android:id/button1").click()

        if self.device(description="dial pad").wait.exists():
            self.device(description="dial pad").click.wait()
        if self.device(description="key pad").wait.exists():
            self.device(description="key pad").click.wait()
        self.device.delay(1)
        # self.device(resourceId="com.tct.dialer:id/digits").long_click()
        self.device.wait("idle")
        for i in code_number:
            self.device(text=i, resourceId="com.tct.dialer:id/dialpad_key_number").click()
        self.device.wait("idle")

    def dialer_num(self, number):
        """
        start a call via dialer number
        :param number:
        :return:
        """
        self.dialer_secret_code(number)
        start_call_btn = self.device(resourceId="com.android.dialer:id/dialpad_floating_action_button")
        assert start_call_btn.wait.exists(), "******** can not find start call btn  ********"
        start_call_btn.click.wait(timeout=3000)

        # verify
        assert self.device(resourceId="com.android.dialer:id/incall_end_call").wait.exists(timeout=3000), \
            "******** dialer failed, can not find end call btn ********"

    def end_call(self, device="m"):
        """m or s device end the call
        arg: device(str) "m" or "s"
        """
        self.logger.debug("device end call")
        call_time = random.randint(5, 10)
        if device == "m":
            self.device.delay(call_time)
            self.end_call_btn.click()
            self.adb.close_call_service()
            if self.end_call_btn.wait.gone(timeout=5000):
                self.logger.info("%s-device end call success" % device)
                return True
        elif device == "mu":  # end call via location
            self.device.delay(call_time)
            self.device.click(539, 1999)  # point for Athena
            if self.end_call_btn.wait.gone(timeout=5000):
                self.logger.info("%s-device end call success" % device)
                return True
        else:
            if self.sdevice(text="00:05").wait.exists(timeout=10000):
                self.sdevice(description="End call").click()
            if self.sdevice(description="End call").wait.gone(timeout=5000):
                self.logger.info("%s-device end call success" % device)
                return True
        self.logger.info("%s-device end call failed" % device)
        self.save_fail_img()
        return False

    def add_contact(self, path, name, number, enter=False):
        """add contact
        arg: Path("Phone" or "SIM") contact saved path
             name(str) contact saved name
             number(str) contact number
        return: True/False
        """
        self.logger.debug("Add contacts {} to {}".format(name, path))
        if enter:
            self.enter_contacts()
        self.float_btn.click.wait()
        el = self.device(text='First name', className="android.widget.EditText")
        el.set_text(name)
        el = self.device(text='Phone', className="android.widget.EditText")
        el.set_text(number)
        self.device(resourceId='com.google.android.contacts:id/menu_save', text="Save").click()
        self.device.delay(2)
        self.device.press.back()
        el = self.search_contact(name)
        success = el.ext5
        if success:
            self.logger.info('add contacts {} successfully'.format(name))
        else:
            self.save_fail_img()
            self.logger.info('add contacts {} failed'.format(name))
        self.quit_search()
        return success

    def delete_contact(self, name, enter=False):
        """delete contact
        arg: name(str) contact name
             enter(boolean) whether need to open contacts
        return: True/False
        """
        self.logger.debug("delete contact %s" % name)
        # if enter:
        self.enter_contacts()
        el_contact = self.search_contact(name)
        # el.left(className="android.widget.QuickContactBadge").click()
        el_contact.click()
        self.device.wait.idle()

        # delete
        self.logger.info('delete contact {}'.format(name))
        self.click_more()
        # self.click_item_in_more('Delete this contact')
        # self.device.delay(1)
        # android.widget.FrameLayout 找不到元素
        # if self.device(text="Delete selected contacts?").exists:
        #     self.logger.info("del popup")
        self.device.delay(1)
        if self.device(text="Delete").exists:
            self.device(text="Delete").click()
        if self.device(text="Delete", resourceId="android:id/button1").exists:
            self.device(text="Delete", resourceId="android:id/button1").click()
        self.device.delay(1)

        # verify
        success = not el_contact.exists
        if success:
            self.logger.info('delete contact {} success'.format(name))
        else:
            self.logger.info('delete contact {} failed'.format(name))
            self.save_fail_img()
        self.quit_search()
        return success

    def click_more(self):
        self.device(description="More options").click()
        self.device.wait.idle()

    def click_item_in_more(self, item):
        self.device(text=item).click()
        self.device.wait.idle()

    def search_contact(self, contact):
        assert self.device(resourceId="com.google.android.contacts:id/open_search_bar_text_view").ext5
        self.device(resourceId="com.google.android.contacts:id/open_search_bar_text_view").click()
        assert self.device(
            resourceId='com.google.android.contacts:id/open_search_view_edit_text').ext5, "not found com.google.android.contacts:id/open_search_view_edit_text"
        self.device(resourceId='com.google.android.contacts:id/open_search_view_edit_text').set_text(contact)
        self.device.delay(1)
        return self.device(resourceId='com.google.android.contacts:id/cliv_name_textview', text=contact)

    def quit_search(self):
        self.device(description='Open navigation drawer').click()

    def back_to_call_app(self, call_type):
        if call_type == "Contact":
            self.back_to_contact()
        else:
            pass

    def end_call_tasking(self,is_multi):
        if is_multi:
            return self.sdevice_end_call() or self.back_end_call()
        else:
            return self.back_end_call()

    def end_call_from_dialer(self):
        self.enter_dialer()
        if self.device(text="Return to call in progress").ext5:
            self.device(text="Return to call in progress").click()
        if self.device(resourceId="com.tct.dialer:id/incall_end_call").ext5:
            self.device(resourceId="com.tct.dialer:id/incall_end_call").click()
            self.logger.debug("end call successfully")
        self.logger.debug("end call completed")
        return True

    def start_call_app(self, call_type):
        """arg: call_type ("Dialer"、"Contact"、"History")
        """
        if call_type == "Contact":
            self.enter_contacts()
        else:
            self.enter_dialer()

    def make_call_from_dialer(self,s_tel):
        self.logger.debug("Dial Number %s." % self.sdevice_tel)
        if self.call_btn.exists:
            pass
        elif self.key_pad.exists:
            self.key_pad.click.wait()
            self.device.wait.idle()

        # input number
        for num in s_tel:
            el = self.device(text=num, resourceId='com.google.android.dialer:id/dialpad_key_number')
            el.click()

        self.device.wait.idle()
        # make call
        self.device.delay(5)
        if self.call_btn().exists:
            self.call_btn.click()

    def make_call_from_contact(self, index):
        contact_name = "AutoTest%02d" % (index + 1)
        self.logger.debug("make call from contact %s" % contact_name)
        self.device(scrollable=True).scroll.vert.to(textStartsWith=contact_name)
        index = 0
        while not self.device(textStartsWith=contact_name).wait.exists() and (index < 10):
            index += 1
            self.device.swipe(500, 2061, 500, 500, 100)
            self.device.wait("idle")

        if self.device(textStartsWith=contact_name).exists:
            self.device(textStartsWith=contact_name).click()
            self.device.delay(2)
        else:
            self.logger.error("Cannot find the contact %s" % contact_name)
            self.save_fail_img()
            return False

        # call contact
        self.device(resourceId='com.google.android.contacts:id/verb_call').click.wait(timeout=2000)

    def sdevice_end_call(self):
        self.logger.info("s-device HANG UP")
        if self.sdevice(text="HANG UP").wait.exists(timeout=30000):
            self.sdevice(text="HANG UP").click()
            self.logger.info("s-device HANG UP successfully")
            self.sdevice.delay(1)
            return True
        else:
            self.logger.info("s-device end call failed")
            self.save_fail_img_s()
            return False

    def sdevice_answer_call(self):
        self.logger.info("s-device answer call")
        if self.sdevice(text="Incoming call").wait.exists(timeout=30000):
            self.logger.info("s-device incoming call")
            self.sdevice.delay(1)
            self.sdevice(description="Answer").click()
            return True
        else:
            self.logger.info("s-device answer call failed")
            self.save_fail_img_s()
            return False

    def call_smart(self, call_type, index=0, open_app=False, multi=False,s_tel=""):
        """
        this method will call the proper carrier service number
        :param call_type:
        :param index:
        :param sim_card:
        :param open_app:
        :param multi:
        :return:
        """
        self.logger.debug("smart call from %s" % call_type)
        if multi:
            self.sdevice.open.notification()
        if call_type == "Dialer":
            if open_app:
                self.enter_dialer()
            self.make_call_from_dialer(s_tel)
        elif call_type == "Contact":
            if open_app:
                self.enter_contacts()
            self.make_call_from_contact(index)
        else:  # history
            if open_app:
                self.enter_dialer()
            self.device(resourceId='com.google.android.dialer:id/call_log_tab').click()
            self.device(resourceId="com.google.android.dialer:id/new_call_log_entry_card", index=1).child(
                resourceId="com.google.android.dialer:id/call_button").click()

        if multi:
            self.sdevice_answer_call()

        # verify, can not check resource id sometimes, add 2 resource to check
        # to_check = [self.device(resourceId="com.tct.dialer:id/contactgrid_contact_name"), ]
        # for view in to_check:
        if self.device(resourceId='com.google.android.dialer:id/incall_end_call').ext5 or \
                self.device(resourceId="com.google.android.dialer:id/contactgrid_contact_name").ext5:
            self.logger.debug("Outgoing call success from %s" % call_type)
            return True

        self.logger.debug("Outgoing call failed from %s" % call_type)
        self.save_fail_img()
        self.device.press.back()
        return False

    def call(self, call_type, index=0, sim_card=1, open_app=False, mutil=False):
        """
        m-device call s-device from Dialer、Contact、History
        return: True/False
        :param call_type: "Dialer"、"Contact"、"History"
        :param index: call in the contact list which one contact
        :param sim_card: if Dual sim card mode,select 1 or 2
        :param open_app:
        :param mutil: True, answer from S device, False, just call 10010
        :return:
        """
        """
        """
        self.logger.debug("call from %s" % call_type)
        if mutil:
            self.sdevice.open.notification()
        if call_type == "Dialer":
            if open_app:
                self.enter_dialer()
            # if self.device(description="dial pad").wait.exists():
            # change to key pad, for Athena Phone 12.0.167196395
            if self.device(description="key pad").wait.exists():
                self.device(description="key pad").click.wait()
            if not mutil:
                self.sdevice_tel = "10010"
            self.logger.debug("Dial Number %s." % self.sdevice_tel)

            # process multi resource id
            number_btn_id = "com.android.dialer:id/dialpad_key_number"
            if not self.device(resourceId=number_btn_id).wait.exists():
                number_btn_id = "com.google.android.dialer:id/dialpad_key_number"

            for i in self.sdevice_tel:
                self.device(text=i, resourceId=number_btn_id).click()
            self.device(description="dial").click()
        elif call_type == "Contact":
            if open_app: self.enter_contacts()
            contact_name = "AutoTest%02d" % (index + 1)
            self.logger.debug("make call from contact %s" % contact_name)
            # self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
            index = 0
            while not self.device(textStartsWith=contact_name).wait.exists() and (index < 10):
                index += 1
                self.device.swipe(840, 1350, 840, 450, 100)
                self.device.wait("idle")
            # self.device(resourceId="com.blackberry.contacts:id/tab_pager", scrollable=True).scroll.vert.to(textStartsWith=contact_name)
            if self.device(textStartsWith=contact_name).exists:
                self.device(textStartsWith=contact_name).click()
                self.device.delay(2)
            else:
                self.logger.warning("Cannot find the contact %s" % contact_name)
                self.save_fail_img()
                return False
            self.device(resourceId='com.blackberry.contacts:id/communication_card').click.wait(timeout=2000)
        else:
            if open_app: self.enter_dialer()
            self.device(description=self.appconfig("recent", "Dialer")).click()
            # self.device(resourceId="com.android.dialer:id/primary_action_button").click.wait(timeout=2000)
            # change to Athena Phone(GMS?) 12.0.167196395
            primary_action_button = self.device(resourceId="com.android.dialer:id/primary_action_button")
            if not primary_action_button.wait.exists():
                primary_action_button = self.device(resourceId="com.google.android.dialer:id/primary_action_button")
            primary_action_button.click.wait(timeout=2000)
        if self.device(resourceId="android:id/select_dialog_listview").wait.exists(timeout=1000):
            self.device(resourceId="android:id/select_dialog_listview").child(index=sim_card - 1).click()
        if mutil:
            self.logger.info("s-device answer call")
            if self.sdevice(text="Incoming call").wait.exists(timeout=30000):
                self.logger.info("s-device incoming call")
                self.sdevice.delay(1)
                self.sdevice(description="Answer").click()
            else:
                self.logger.info("s-device answer call failed")
                self.save_fail_img_s()
                return False
        # todo: should check telephony status first??
        if self.device(description="End call").wait.exists(timeout=5000):
            self.logger.debug("Outgoing call success from %s" % call_type)
            return True
        self.logger.debug("Outgoing call failed from %s" % call_type)
        self.save_fail_img()
        self.sdevice.press.back()
        return False

    def call_10010(self, call_type, index=0, sim_card=1, open_app=False):
        """m-device call 10010 from Dialer、Contact、History
        arg: call_type(Dialer、Contact、History)
             index(int) Call in the contact list which one contact
             sim_card(int) if Dual sim card mode,select 1 or 2
        return: True/False
        """
        self.logger.debug("call from %s" % call_type)
        if call_type == "Dialer":
            if open_app: self.enter_dialer()
            packagename = self.device.info["currentPackageName"]
            # if open_app:self.enter_dialer()
            self.logger.debug("Dial Number 10010.")
            if self.device(description="key pad").wait.exists():
                self.device(description="key pad").click.wait()
            for i in "10010":
                self.device(text=i, resourceId="%s:id/dialpad_key_number" % packagename).click()

            # sim_res = 'com.tct.dialer:id/sim_0{}_dial_btn'.format(sim_card)
            sim_res = 'com.google.android.dialer:id/dialpad_floating_action_button'
            self.device(resourceId=sim_res).click()

            # if self.device(resourceId="com.android.dialer:id/multi_dial_button").wait.exists(timeout=3000):
            #     self.device(resourceId="com.android.dialer:id/dial_sim_%s" % sim_card).click()
            # else:
            #     self.device(description="dial").click()
        elif call_type == "Contact":
            if open_app:
                self.enter_contacts()

            contact_name = "AutoTest%02d" % (index + 1)
            self.logger.debug("make call from contact %s" % contact_name)
            self.device(scrollable=True).scroll.vert.to(textStartsWith=contact_name)
            index = 0
            while not self.device(textStartsWith=contact_name).wait.exists() and (index < 10):
                index += 1
                self.device.swipe(500, 2061, 500, 500, 100)
                self.device.wait("idle")
            if self.device(textStartsWith=contact_name).exists:
                self.device(textStartsWith=contact_name).click()
                self.device.delay(2)
            else:
                self.logger.error("Cannot find the contact %s" % contact_name)
                self.save_fail_img()
                return False
            self.device(resourceId='com.google.android.contacts:id/verb_call').click.wait(timeout=2000)

        else: #history
            if open_app:
                self.enter_dialer()
            el = self.device(resourceId='com.google.android.dialer:id/primary_action_button')
            el.click()

        if self.device(resourceId="android:id/select_dialog_listview").wait.exists(timeout=1000):
            self.device(resourceId="android:id/select_dialog_listview").child(index=sim_card - 1).click()
        if self.device(description="End call").wait.exists(timeout=10000):
            self.logger.debug("Outgoing call success from %s" % call_type)
            return True
        self.logger.debug("Outgoing call failed from %s" % call_type)
        self.save_fail_img()
        self.device.press.back()
        return False

    def s_call(self):
        """s-device call m-device from Dialer"""
        self.logger.info("s_device call m_device")
        data = self.sdevice.server.adb.shell("am start -a android.intent.action.CALL -d tel:%s" % self.mdevice_tel)
        if data.find("Error") > -1:
            self.logger.error("Fail to call m-device.")
            return False
        self.device.open.notification()
        if self.device(textContains="Incoming call").wait.exists(timeout=20000):
            self.logger.info("m-device incoming call")
            self.device(text="ANSWER").click()
            # if self.device(description="Dialpad").wait.exists(timeout=5000):
            self.logger.debug("m_device Outgoing call success")
            return True
        self.logger.debug("m_device Outgoing call failed")
        self.save_fail_img()
        return False

    def answer_musicing(self):
        """m-device answer s-device call during play music
        return: True/False
        """
        if self.s_call():
            self.logger.debug("answer call during play music success")
            return True
        self.logger.debug("answer call during play music failed")
        return False

    def back_music(self):
        """m-devices close music
        return: True/False
        """
        self.logger.info("back to music and close music")
        # if self.device(packageName="com.google.android.music").wait.exists():
        #     self.logger.info("back music success")
        #     return self.is_playing_music()
        # else:
        #     self.logger.info("back music failed")
        #     self.save_fail_img()
        #     return False
        if self.device(packageName="com.tct.music").wait.exists():
            self.logger.info("back music success")
            return self.is_playing_music()
        else:
            self.logger.info("back music failed")
            self.save_fail_img()
            return False

    def get_phone_num(self):
        """
        get phone number from phone app
        :return:
        """
        try:
            self.logger.debug("try to get phone number")
            assert self.device(resourceId="com.android.dialer:id/my_number").wait.exists(), \
                "******** can find phone number  ********"
            ret = self.device(resourceId="com.android.dialer:id/my_number").get_text()
            self.logger.debug("phone number: %s" % str(ret))
            temp = ret.split("+86")[1]
            phone_num = temp if self.verify_phone_num(temp) else ""
        except:
            self.logger.warning(traceback.format_exc())
            self.save_fail_img()
            phone_num = ""
        # print phone_num
        return phone_num

    def verify_phone_num(self, number):
        p2 = re.compile("1\d{10}")
        match = p2.match(number)
        ret = True if match else False
        return ret

    def process_call_in_notification(self, action):
        """
        process call in notification, dismiss or answer
        :param action:
        :return:
        """
        assert self.device(textStartsWith="Incoming call").wait.exists(timeout=30000), \
            "******** can not find incoming call  ********"

        current_action = self.device(text=action)
        assert current_action.wait.exists(), "******** can not find action:%s  ********" % action
        current_action.click.wait(timeout=3000)

    def end_call_now(self):
        """
        end call now
        :return:
        """
        end_call = self.device(description="End call")
        assert end_call.wait.exists(timeout=5000), "***** can not find end call btn"
        end_call.click()
        assert end_call.wait.gone(timeout=2000), "***** end call failed"
        self.logger.info("end call success")

    def silence_call(self):
        """
        slience call when call coming
        :return:
        """
        assert self.device(textStartsWith="Incoming call").wait.exists(timeout=30000), \
            "******** can not find incoming call  ********"
        self.device.press.volume_down()
        # todo: how to verify the ring gone?

    def send_sms(self, number, msg):
        """
        can not use sms manager......
        :param number:
        :param msg:
        :return:
        """
        ret, _ = self.adb.shell2("am start -a android.intent.action.SENDTO -d sms:%s --es sms_body  %s" % (number, msg))
        print ret
        self.device.delay(1)
        send_btn = self.device(resourceId="com.google.android.apps.messaging:id/send_message_button_icon")
        assert send_btn.wait.exists(), "******** can not find send btn  ********"
        send_btn.click.wait(timeout=3000)
        self.device.press.back()

    def clear_all_phone_calls(self):
        """
        clear phone call,
        first, try to close phone calls via API
        second, try to close phone calls via UI, find text/location
        :return:
        """
        if not self.adb.close_call_service():
            self.enter_dialer()
            if self.device(text="Return to call in progress").wait.exists(timeout=2000):
                if self.device(text="Return to call in progress").click.wait():
                    end_call = self.device(description="End call")
                    if end_call.wait.exists(timeout=5000):
                        end_call.click()
                    else:
                        self.device.click(522, 1443)

if __name__ == '__main__':
    a = Telephony ("GAWKFQT8WGL7L7S8", "telephony")
    a.call_btn.click()