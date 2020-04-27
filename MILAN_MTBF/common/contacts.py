#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: contacts.py
@time: 2017/10/10 18:35

information about this file
"""

from common import *


class Contacts(Common):
    app_name = 'Contacts'
    package = 'com.tct.contacts'
    launch_activity = 'com.android.contacts.activities.PeopleActivity'

    def setup(self, device_id):
        if self.config.site == "US":
            sdevice_tel, sdevice_msg = self.get_tel_number(device_id)
        else:
            sdevice_tel = self.get_carrier_service_num()
            if sdevice_tel not in ['10010', '10000', '10086']:
                self.logger.error('service num not found no vCard to import')
                return

        vcf_name = '{}.vcf'.format(sdevice_tel)
        self.logger.debug("open %s file" % vcf_name)
        vcf_file = os.path.join(
            self.project_root(),
            'StabilityResource',
            vcf_name
        )
        self.logger.info('push vcf file {}'.format(vcf_name))
        self.adb.cmd('push', vcf_file, '/sdcard')
        # self.delete_all_contacts()
        self.device.delay(1)

        self.start_app("File Manager")
        if self.device(text="ALLOW").exists:
            self.device(text="ALLOW").click()
        self.device.delay(1)
        if self.device(resourceId="com.jrdcom.filemanager:id/guide_close").exists:
            self.device (resourceId="com.jrdcom.filemanager:id/guide_close").click()
        if self.device(text="Internal storage").exists:
            self.device(text="Internal storage").click()

        self.device(scrollable=True).scroll.vert.to(text=vcf_name)
        self.device(text=vcf_name).click()
        if self.device(text="Device").exists:
            self.device (text="Device").click()
        if self.device(text="Contacts").exists:
            self.device(text="Contacts").click()
            if self.device(text="ALWAYS").exists:
                self.device (text="ALWAYS").click()
            if self.device(text="ALLOW").exists:
                self.device (text="ALLOW").click()
            if self.device (text="OK").exists:
                self.device (text="OK").click ()
        elif self.device(text="Import contacts from vCard?").exists:
            self.device(text="OK").click()
        self.logger.debug("import %s file successfully" % vcf_name)

        self.clear(self.package)
        self.start_app(self.app_name)
        el = self.device(text='IMPORT CONTACTS')
        if el.wait.exists(timeout=10000):
            el.click.wait()
            self.allow_permissions()
            self.logger.info('select import from')
            el = self.device(text='Internal shared storage')
            el.click.wait()
            el = self.device(textMatches='next|NEXT')
            el.click.wait()
            self.logger.info('select import to')
            el = self.device(text='Phone')
            el.click.wait()
            el = self.device(textMatches='next|NEXT')
            el.click.wait()
            el = self.device(text=vcf_name)
            el.click.wait()
            el = self.device(textMatches='ok|OK')
            el.click.wait()

    def delete_all_contacts(self):
        self.start_app(self.app_name)
        # switch to 3 tab
        for i in range(100):
            el = self.device(text='Contact list is empty')
            if el.exists:
                self.logger.info('empty contact list')
                break
            try:
                el = self.device(textStartsWith='Auto')
                self.logger.info('delete contact {}'.format(el.get_text()))
                el.click()
                el = self.device(text='Delete this contact')
                el.click()
                el = self.device(textMatches='delete|DELETE')
                el.click()
            except Exception:
                break
        self.logger.info('done delete all contacts')

    def enter_and_dismiss_if_need(self):
        """Launch Contacts by StartActivity.
        """
        self.logger.debug("Launch Contacts.")
        self.start_app("Contacts")

        if self.device(text="Contacts by BlackBerry").wait.exists():
            assert self.device(
                resourceId="com.blackberry.contacts:id/intro_skip_button").wait.exists(), "******** can not find skip btn ********"
            self.device(resourceId="com.blackberry.contacts:id/intro_skip_button").click()
            self.device(resourceId="com.blackberry.contacts:id/intro_skip_button").wait.gone(timeout=3000)
            if self.device(resourceId="com.blackberry.contacts:id/drawer_container").wait.exists(timeout=3000):
                return self.back_to_contacts_home()

        return self.device(description="Compose button", packageName="com.blackberry.hub").wait.exists(
            timeout=self.timeout)

    def back_to_contacts_home(self):
        """
        back to contacts home
        @return:
        """
        self.logger.info("try to back to contacts home within 5 steps")
        for step in range(5):
            if not self.is_contact_home():
                self.device.press.back()
                self.device.delay(1)
            else:
                return True
        else:
            self.save_fail_img()
            self.logger.error("***** can not back to contacts home within 5 steps *****")
            return False

    def delete_contact_if_exists(self, contact):
        """
        del contact, search contact first, if exist, del, if not exist, return false
        :param contact:
        :return:
        """
        # search contact first
        try:
            if self.search_contact(contact):
                # self._perform_edit_action()
                self._perform_del_action()

                assert not self.device(resourceId="com.blackberry.contacts:id/cliv_name_textview",
                                       text=contact).wait.exists(timeout=3000), "contact del failed"
        except ContactNotFoundException:
            self.back_to_contacts_home()

    def search_contact(self, contact):
        """
        search contact
        :param contact:
        :return:
        """
        self.logger.info("searching %s" % contact)
        if not self.is_contact_home():
            self.enter_and_dismiss_if_need()
        self.back_to_contacts_home()
        assert self.is_contact_home(), "***** can not open contact home *****"

        self.device(resourceId="com.blackberry.contacts:id/menu_search").click()

        # fill in contact
        search_view = self.device(resourceId="com.blackberry.contacts:id/search_view")
        assert search_view.wait.exists(), "******** can not open search view  ********"
        search_view.set_text(contact)

        # click result
        if self.device(resourceId="com.blackberry.contacts:id/cliv_name_textview", text=contact).wait.exists(
                timeout=3000):
            self.device(resourceId="com.blackberry.contacts:id/cliv_name_textview").click()
            self.device(resourceId="com.blackberry.contacts:id/cliv_name_textview").wait.gone()
            return True
        else:
            self.logger.error("******* can not find contact: %s ******" % contact)
            raise ContactNotFoundException

    def is_contact_home(self):
        """
        check contact home
        :return:
        """
        search_btn = self.device(resourceId="com.blackberry.contacts:id/menu_search")
        floating_action_btn = self.device(resourceId="com.blackberry.contacts:id/floating_action_button")
        return floating_action_btn.wait.exists(timeout=2000) and search_btn.wait.exists(timeout=1000)

    def _perform_del_action(self):
        """
        perform del action in edit activity
        :return: 
        """

        edit_btn = self.device(resourceId="com.blackberry.contacts:id/menu_delete")
        assert edit_btn.wait.exists(), "******** can not find delete btn ********"
        edit_btn.click.wait(timeout=3000)

        # confirm
        ok_btn = self.device(resourceId="android:id/button1")
        assert ok_btn.wait.exists(), "******** can not find OK btn ********"
        ok_btn.click.wait(timeout=3000)

    def _perform_edit_action(self):
        """
        perform edit action in contact details activity
        :return:
        """
        edit_btn = self.device(resourceId="com.blackberry.contacts:id/menu_edit")
        assert edit_btn.wait.exists(), "******** can not find edit menu ********"
        edit_btn.click.wait(timeout=3000)

    def create_contact(self, account, contact, nickname, tel_num="13143344"):
        """

        :param account:
        :param contact:
        :param nickname:
        :param tel_num:
        :return:
        """
        self.logger.info("creating contact %s" % contact)
        if not self.is_contact_home():
            self.enter_and_dismiss_if_need()
        self.back_to_contacts_home()
        assert self.is_contact_home(), "***** can not open contact home *****"

        floating_action_btn = self.device(resourceId="com.blackberry.contacts:id/floating_action_button")
        floating_action_btn.click.wait()

        # select account
        account_select = self.device(text=account)
        assert account_select.wait.exists(), "******** can not find account %s to create contact ********" % account
        account_select.click.wait(timeout=3000)

        # set name, nickname, phone
        assert self.device(text="Name").wait.exists(timeout=3000), "can not find 'Name' input box"
        self.device(text="Name").set_text(contact)
        self.device(text="Nickname").set_text(nickname)
        if not self.device(text="Phone").exists:
            self.device(resourceId="com.blackberry.contacts:id/editors").swipe.up(steps=30)
        self.device(text="Phone").set_text(tel_num)

        self.device.delay(1)

        # save contact
        self.device(resourceId="com.blackberry.contacts:id/menu_save").click()

        # verify
        assert self.back_to_contacts_home(), "can not back to contact home after create contact"
        assert self.device(text=contact).wait.exists(timeout=1000), "can not find contact created just now"

    def edit_nickname(self, contact, nickname_old, nickname_new):
        """
        edit nickname
        :param contact:
        :param nickname:
        :return:
        """
        self.logger.info("editing nickname %s" % contact)
        try:
            if self.search_contact(contact):
                self._perform_edit_action()
                self.device(text=nickname_old).set_text(nickname_new)
                self.device(resourceId="com.blackberry.contacts:id/menu_save").click()

                # verify
                edit_btn = self.device(resourceId="com.blackberry.contacts:id/menu_edit")
                assert edit_btn.wait.exists(), "******** can not find edit menu after edit nickname********"
                assert self.device(text=nickname_new).wait.exists(timeout=3000), "edit nickname failed"
        except:
            raise


class ContactNotFoundException(Exception):
    def __init__(self, err='contact not found'):
        Exception.__init__(self, err)


if __name__ == '__main__':
    a = Contacts("2cd0e633", "calendar")
    print a.device.dump(r"c:\recorder.xml")
