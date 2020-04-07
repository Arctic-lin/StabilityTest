# -*- coding: utf-8 -*-
"""message library for scripts.
"""
from common import *
from google_music import google_Music
from native_music import native_Music

class Message(Common):
    app_name = 'Messages'
    package = 'com.google.android.apps.messaging'
    launch_activity = '.ui.ConversationListActivity'

    def __init__(self, device, log_name, sdevice=None):
        Common.__init__(self, device, log_name, sdevice)
        self.music = native_Music(self.device, "msg_music")
        self.appconfig.set_section("Message")
        self.msgs = {'MMS': "1111", 'SMS': "4444"}
        self.msgs_check = {'MMS': True, 'SMS': False}
        self.start_new_conv_btn = self.device(
            resourceId='com.google.android.apps.messaging:id/start_new_conversation_button')

    def setup(self):
        self.clear(self.package)
        self.start_app(self.app_name,b_desk=False)
        if self.device(text="New! Spam protection").exists:
            self.device(text="OK").click()
        self.close_notification()
        self.delete_extra_msg()
        if not self.get_carrier_service_num():
            self.logger.info('no sim card can not send messages')
            return
        self.send_msg_to('1111', '1111', True)
        self.send_msg_to('4444', '4444', False)

    def close_notification(self):
        if self.device (description="More options").wait.exists (timeout=3000):
            self.device(description="More options").click()
        if self.device(text="Settings").wait.exists (timeout=3000):
            self.device(text="Settings").click()
        self.device(text="Notifications").click()
        status = self.device(text="On").sibling(resourceId="com.android.settings:id/switch_widget").get_text()
        if status.lower() == "on":
            self.device(text="On").sibling(resourceId="com.android.settings:id/switch_widget").click()
        else:
            self.logger.debug("Message notification is already close")


    def enter(self):
        """Launch messaging.
        """
        self.logger.debug('enter Message')
        if self.start_new_conv_btn.wait.exists(timeout=2000):
            return True
        self.start_app(self.app_name)
        return self.start_new_conv_btn.wait.exists(timeout=2000)

    def enter_new(self):
        """Launch messaging.
        """
        self.logger.debug('enter Messages')
        self.stop_app(self.package)
        if self.start_new_conv_btn.wait.exists(timeout=2000):
            return True
        self.start_app(self.app_name)
        if self.device(text='SKIP').wait.exists():
            self.device(text='SKIP').click.wait()

        if self.device(text="Not now").wait.exists(timeout=1000):
            self.device(text="Not now").click.wait()
        return self.start_new_conv_btn.wait.exists(timeout=2000)

    def back_to_message(self):
        """back to message list .
        """
        self.logger.debug('Back to message list')
        for i in range(5):
            if self.start_new_conv_btn.wait.exists(timeout=2000):
                return True
            self.device.press.back()
            self.device.delay(1)
        else:
            self.logger.warning('Back to message list fail')
            return self.enter()

    def back_to_messages(self):
        self.logger.debug('Back to Messages list')
        for i in range(5):
            if self.device(text='Messages').exists:
                break
            self.device.press.back()
        else:
            self.logger.warning('Back to Messages list fail')
            self.enter()

    def s_send_msg(self, loop=0):
        """s-device send message to m-device
        """
        contentm = "Message test loop %d" % (loop + 1)
        self.logger.info("s-device send %s to m-device" % contentm)
        data = self.sdevice.server.adb.shell("am start -a android.intent.action.SENDTO -d sms:%s" % self.mdevice_msg)
        if data.find("Error") > -1:
            self.logger.error("Fail to send a sms to m-device.")
            return False
        self.device.delay(2)
        self.sdevice(resourceId="com.android.mms:id/embedded_text_editor").set_text(contentm)
        self.sdevice(description="Send").click()
        self.logger.debug("M-device receive msg")
        self.device.open.notification()
        if self.device(text=contentm).wait.exists(timeout=180000):
            self.logger.info("s-device send %s to m-device success" % contentm)
            return True
        else:
            self.logger.info("s-device send %s to m-device failed" % contentm)
            self.save_fail_img()
            return False

    def answer_musicing(self, loop=0):
        """answer s-device message during play music
        """
        contentm = "Message test loop %d" % (loop + 1)
        contents = "Already receive message %d" % (loop + 1)
        self.logger.info("m-device reply %s to s-device and back to music" % contents)
        self.device(text=contentm).click()
        self.device.delay(2)
        self.logger.info("mdvice replay msg %s to sdevice" % contents)
        self.device(resourceId="com.android.mms:id/embedded_text_editor").set_text(contents)
        self.device(description="Send").click()
        self.logger.debug("s-device receive msg")
        if self.sdevice(text=contents).wait.exists(timeout=180000):
            self.logger.info("mdvice replay msg %s to sdevice success" % contents)
            self.logger.info("mdevice back to music")
            for i in range(5):
                self.device.press.back()
                if self.device(packageName="com.tct.music").wait.exists(timeout=2000):
                    self.logger.info("mdevice back to music success")
                    return True
            self.logger.info("mdevice back to music failed")
            self.save_fail_img()
            self.start_app("Music", False)
            return False
        else:
            self.logger.info("mdvice replay msg %s to sdevice failed" % contents)
            self.save_fail_img()
            self.device.press.back()
            return False

    def _verify_msg_sending(self):
        """verify whether the message has received
        """
        self.logger.info("verify send message result")
        self.device(textStartsWith='Sending').wait.gone(timeout=18000)
        if self.device(text='Now • SMS').wait.exists():
            self.logger.debug('message send success!')
            return True
        elif self.device(text='Now • MMS').wait.exists():
            self.logger.debug('message send success!')
            return True
        elif self.device(text='Now').wait.exists():
            self.logger.debug('message send success!')
            return True
        else:
            self.device.press.back()
            if self.device(textContains='Now').wait.exists(timeout=18000):
                self.logger.debug('message send success!')
                return True
            self.logger.error('message send fail!!!')
            self.save_fail_img()
            return False

    def select_msg(self, strtype):
        """select message by specified index.
        arg:(str)strtype -- for stability test.
                 msgs = {'MMS':2,'SMS':1}
        """
        conv_name = self.msgs[strtype]
        self.logger.info('select msg {}'.format(conv_name))
        el = self.device(resourceId='com.google.android.apps.messaging:id/conversation_name', text=conv_name)
        if el.exists:
            el.click.wait()
        el = self.device(resourceId='com.google.android.apps.messaging:id/conversation_title', text=conv_name)
        if not el.exists:
            self.logger.error('select msg {} failed'.format(conv_name))
            return False
        return True

    def save_draft(self, msg_type, number, need_send=False):
        """save and send draft message
        arg: msg_type(str) SMS or MMS
        """
        self.logger.debug("Save a %s draft message." % (msg_type))
        self.device(resourceId="com.google.android.apps.messaging:id/start_new_conversation_button").click()
        self.logger.debug("Add a recipient.")
        self.device.wait("idle")
        # you can add a recipient from contacts
        # self.device(resourceId="com.android.mms:id/recipients_picker").click()
        # self.device.delay(2)
        # recipient = self.device(resourceId="android:id/list").child(index=0).child(index=2).get_text()
        # self.device(resourceId="android:id/list").child(index=0).click()
        # self.logger.info("recipient is %s" % recipient)
        # self.device(resourceId="com.android.contacts:id/done").click()

        if self.device(text="ASK FOR PERMISSION").wait.exists(timeout=4000):
            self.device(text="ASK FOR PERMISSION").click.wait()
            if self.device(text="ALLOW").exists:
                self.device(text="ALLOW").click.wait()
        self.device(resourceId="com.google.android.apps.messaging:id/recipient_text_view").set_text(number)
        self.device.delay(2)
        self.device.press.enter()
        self.device.delay(2)

        # prepare draft
        if self.device(description="Confirm participants").wait.exists(timeout=2000):
            self.device(description="Confirm participants").click.wait()
            self.device.delay(2)
        if msg_type == "SMS":
            self.logger.info("save a text sms")
            self.device(resourceId="com.google.android.apps.messaging:id/compose_message_text").set_text(
                "Test message 0123456789!!!")
        if msg_type == "MMS":
            i = random.randint(2, 3)
            self.device(resourceId="com.google.android.apps.messaging:id/compose_message_text").set_text(
                "Go Spurs Go 0123456789!!!")
            self.device.delay(2)
            self.device(resourceId="com.google.android.apps.messaging:id/attach_media_button").click()
            if i == 1:
                self.logger.info("save a picture mms")
                self.device(description="Capture pictures or video").click()
                self.device.delay(1)
                # self.device(resourceId="com.android.mms:id/take_picture").click()
                if self.device(text="ALLOW").exists:
                    self.device(text="ALLOW").click()
                    self.device.delay()
                if self.device(text="OK", className="android.widget.Button").exists:
                    self.device(text="OK", className="android.widget.Button").click()
                    self.device.delay()
                self.device(description="Take picture").click()
                # self.device(resourceId="com.android.mms:id/button_done").click.wait(timeout=2000)
            elif i == 2:
                self.logger.info("save a video mms")
                self.device(description="Capture pictures or video").click()
                self.device.delay(1)
                # self.device(resourceId="com.android.mms:id/take_picture").click()
                if self.device(text="ALLOW").exists:
                    self.device(text="ALLOW").click()
                    self.device.delay()
                if self.device(text="OK", className="android.widget.Button").exists:
                    self.device(text="OK", className="android.widget.Button").click()
                    self.device.delay()
                self.device(description="Capture video").click()
                self.device.delay()  # recorder video 4s
                if self.device(resourceId="com.google.android.apps.messaging:id/camera_capture_button").exists:
                    self.device(resourceId="com.google.android.apps.messaging:id/camera_capture_button").click()
                # self.device(resourceId="com.android.mms:id/button_done").click.wait(timeout=2000)
            else:
                self.logger.info("save a audio mms")
                self.device(description="Record audio").click()
                if self.device(text="ALLOW").exists:
                    self.device(text="ALLOW").click()
                    self.device.delay()
                if self.device(text="OK", className="android.widget.Button").exists:
                    self.device(text="OK", className="android.widget.Button").click()
                    self.device.delay()
                x, y = self.device(
                    resourceId="com.google.android.apps.messaging:id/record_button_visual").get_location()
                self.device.swipe(x, y, x + 1, y + 1, 200)
        self.device.delay(2)

        # verify
        if need_send:
            self.device(resourceId="com.google.android.apps.messaging:id/send_message_button_icon").click.wait()
        self.back_to_message()
        if need_send and self.device(text="Just now").wait.exists(timeout=5000):
            self.logger.info("send a %s message success!" % msg_type)
            return True
        elif need_send and not self.device(text="Just now").wait.exists(timeout=5000):
            self.logger.info("send a %s message Fail!" % msg_type)
            return False
        elif self.device(text="Draft").exists:
            self.logger.info("Save a %s draft success!" % msg_type)
            return True
        else:
            self.logger.info("Save a %s draft failed!" % msg_type)
            self.save_fail_img()
            return False

    def send_draft(self, msg_type):
        self.logger.info("open %s from draft" % msg_type)
        self.device(text="Draft").click()
        '''if msg_type == "MMS":
            self.device(description="Send Message").click.wait(timeout=2000)
        else:
            self.device(resourceId="com.google.android.apps.messaging:id/send_message_button_icon").click.wait(timeout=2000)'''
        self.device(resourceId="com.google.android.apps.messaging:id/send_message_button_icon").click.wait(timeout=2000)
        # self.device(description="Send Message" if msg_type == "MMS" else "Send").click.wait(timeout=2000)
        return self._verify_msg_sending()

    def fwd_msg(self, msg_type, number, sim_card=1):
        """Long touch a msg in tread screen and select the option.
        """
        self.logger.info("forward %s to %s" % (msg_type, number))
        self.logger.info("Select %s." % msg_type)
        msg = self.msgs[msg_type]
        if not msg:
            self.logger.error('{} unsupported msg type'.format(msg_type))
            return False
        self.create_source_msg_if_needed(msg_type)
        self.select_msg(msg_type)
        self.device.long_click(608, 1269)
        self.device.wait.idle()
        # self.device(resourceId="com.google.android.apps.messaging:id/message_text").long_click()

        el = self.device(description='More options')
        el.click.wait()
        self.device.delay(2)
        el = self.device(text='Forward')
        el.click()
        self.device(textMatches="New message|NEW MESSAGE").click.wait()
        self.device.delay(2)

        # input contact
        self.device(resourceId="com.google.android.apps.messaging:id/recipient_text_view").click()
        self.adb.shell("input keyevent KEYCODE_DEL")
        self.device.wait("idle")
        for i in number:
            self.adb.shell("input text %s" % i)
        self.device.delay(1)
        self.device.press.enter()
        self.device.delay(2)
        if self.device(description="Confirm participants").wait.exists(timeout=2000):
            self.device(description="Confirm participants").click()
            self.device.delay(1)
        el = self.device(resourceId="com.google.android.apps.messaging:id/send_message_button_container")
        el.click.wait(timeout=2000)
        if self.device(text="Select SIM card").wait.exists(timeout=2000):
            self.device(text="Select SIM card").sibling(index=sim_card).click()
        return True

    def create_source_msg_if_needed(self, msg_type):
        msg_text = self.msgs[msg_type]
        el = self.device(resourceId='com.google.android.apps.messaging:id/conversation_name', text=msg_text)
        if el.exists:
            return
        else:
            self.send_msg_to(msg_text, msg_text, self.msgs_check[msg_type])
            self.device.delay(1)
            self.device.press.back()

    def get_sms_num(self):
        """Get the number of messages from the message list
        """
        return self.device(resourceId='com.google.android.apps.messaging:id/conversation_name').count

    def delete_msg(self, name):
        """delete msg from message list
        arg: name(str)  message contact name
        """
        self.device(text=name).click.wait(timeout=2000)
        self.device(description="More options").click.wait(timeout=2000)

        try_items = [self.device(text="Delete"), self.device(text="Discard")]
        self.click_if_exists_in_items(3000, *try_items)

        assert self.device(textMatches="Delete|DELETE").wait.exists(timeout=2000)
        self.device(textMatches="Delete|DELETE").click.wait()
        self.logger.debug("delete %s msg completed!!!" % name)

    def delete_extra_msg(self):
        """ Long press to delete message in the message list
        """
        self.logger.debug("Delete the extra message.")
        self.back_to_messages()
        self.device.delay(2)
        msg_count = self.get_sms_num()
        for i in range(msg_count):
            self.logger.debug("delete invalid message %d times"%(i+1))
            el = self.device(resourceId="android:id/list") \
                .child(index=i, className='android.widget.FrameLayout') \
                .child(resourceId="com.google.android.apps.messaging:id/conversation_name")
            if not el.exists:
                continue
            msg = el.get_text()
            if msg not in self.msgs.values():
                self.delete_msg(msg)
            # msg_count = self.get_sms_num()#如果删除失败会导致一直循环出不去
        return True

    def send_msg_to(self, phone_num, msg, is_mms=False):
        """
        send msg to a given phone number,
        :param phone_num_s:
        :param msg:
        :param param:
        :return:
        """
        assert self.enter_new()
        self.device(resourceId="com.google.android.apps.messaging:id/start_new_conversation_button").click.wait()

        # allow permissions if need
        if self.device(text="ASK FOR PERMISSION").wait.exists(timeout=2000):
            self.device(text="ASK FOR PERMISSION").click.wait()
            if self.device(text="ALLOW").wait.exists(timeout=3000):
                self.device(text="ASK FOR PERMISSION").click.wait()

        # input phone number
        assert self.device(resourceId="com.google.android.apps.messaging:id/recipient_text_view").wait.exists(), \
            "******** can not find textbox to input phone num  ********"
        recipient_el = self.device(resourceId="com.google.android.apps.messaging:id/recipient_text_view")
        recipient_el.click.wait()
        self.device.delay(5)
        self.skip_google_ime_init()
        for char in phone_num:
            self.device.press(int(char) + 7)
        self.device.delay(5)
        self.device.press.enter()
        # input message
        msg_body = self.device(resourceId="com.google.android.apps.messaging:id/compose_message_text")
        assert msg_body.wait.exists(timeout=30000), "******** can not find textbox to input message  ********"
        msg_body.set_text(msg)
        self.device.wait("idle")
        # add multimedia file if needed
        if is_mms:
            self.add_multimedia_file(action="photo")

        # send
        self.device.delay()
        send_btn = self.device(resourceId="com.google.android.apps.messaging:id/send_message_button_icon")
        assert send_btn.wait.exists(), "******** can not find send btn  ********"
        send_btn.click()

        # verify
        self._verify_msg_sending()

    def add_multimedia_file(self, action=""):
        """
        add multimedia file, current now just send a pic from device, maybe we can add more action to add audio, video
        :return: 
        """

        add_btn = self.device(description="Attach from camera or gallery")
        assert add_btn.wait.exists(), "******** can not find + btn ********"
        add_btn.click.wait(timeout=3000)
        if "photo" in action:
            self.take_photo()
            return
        self.device(resourceId="com.google.android.apps.messaging:id/image").click.wait()

    def skip_google_ime_init(self):
        # strange this element use description as text
        el = self.device(description='Help build a better keyboard')
        if el.exists:
            el = self.device(text='NO, THANKS')
            el.click()

    def open_msg_received(self, msg):
        """

        :return:
        """
        assert self.device(text=msg).wait.exists(timeout=30000), "***** can not find received msg*****"
        self.device(text=msg).click.wait()

    def del_msg(self):
        """
        del msg
        :param msg: 
        :return: 
        """
        try:
            menu_btn = self.device(description="More options")
            assert menu_btn.wait.exists(), "******** can not find menu btn ********"
            menu_btn.click.wait(timeout=3000)

            del_option = self.device(text="Delete")
            assert del_option.wait.exists(), "******** can not find del option  ********"
            del_option.click.wait(timeout=3000)

            confirm = self.device(text="DELETE")
            assert confirm.wait.exists(), "******** can not find DELETE dialog ********"
            confirm.click.wait(timeout=3000)
        except:
            self.logger.debug("******* del message failed, but we can ignore this issue ******")
            pass

    def reply_msg(self, msg, is_mms=False):
        """
        reply msg
        :param msg:
        :param is_mms:
        :return:
        """
        # input message
        msg_body = self.device(resourceId="com.google.android.apps.messaging:id/compose_message_text")
        assert msg_body.wait.exists(), "******** can not find textbox to input message  ********"
        msg_body.set_text(msg)

        # add multimedia file if needed
        if is_mms:
            self.add_multimedia_file(action="photo")

        # send
        self.device.delay()
        send_btn = self.device(resourceId="com.google.android.apps.messaging:id/send_message_button_icon")
        assert send_btn.wait.exists(), "******** can not find send btn  ********"
        send_btn.click()

        # verify
        self._verify_msg_sending()

    def take_photo(self):
        """
        take photo in messages
        :return: 
        """
        # attach_media_btn = self.device(resourceId="com.google.android.apps.messaging:id/attach_media_button")
        # assert attach_media_btn.wait.exists(), "**** can find btn for attach media ****"
        # attach_media_btn.click()

        self.device(resourceId = "com.google.android.apps.messaging:id/shutter_button").click()
        self.device.delay(4)
        # self.device(resourceId="com.google.android.apps.messaging:id/shutter_button").click()
        # self.device.delay()

    def download_attachment(self, reply_msg):
        """
        download media
        :param reply_msg:
        :return:
        """
        num = self.get_saved_photos()
        print "current num of saved photos -> %s" % num
        # fail to assert text-reply_msg sometimes, however the error pic show it is in the page.
        media = self.device(resourceId="com.google.android.apps.messaging:id/message_text", text=reply_msg)
        # media = self.device(resourceId="com.google.android.apps.messaging:id/message_attachments")
        assert media.wait.exists(), "******** can not find message: %s  ********" % reply_msg
        x, y = media.get_location()
        self.device.long_click(x, y - 100)

        save = self.device(resourceId="com.google.android.apps.messaging:id/save_attachment")
        assert save.wait.exists(), "******** can not find save btn ********"
        save.click.wait(timeout=3000)

        if self.device(text="ALLOW").wait.exists(timeout=3000):
            self.device(text="ALLOW").click.wait()

        num_new = self.get_saved_photos()
        print "new num of saved photos -> %s" % num_new

        assert num_new > num, "***** save photo failed *****"

    def get_saved_photos(self):
        return self.get_file_num(self.appconfig("storage_path", "Message"), ".jpg")


if __name__ == '__main__':
    a = Message("GAWKFQT8WGL7L7S8", "Message")
    # a.enter()
    # a.save_draft("MMS", "10010")
    # a.send_draft("MMS")
    a.setup()
