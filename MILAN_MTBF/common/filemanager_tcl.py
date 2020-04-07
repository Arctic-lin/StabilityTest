#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2019/5/28 15:40

information about this file
"""

from common import *


class FileManagerTCL(Common):
    """Provide common functions involved TCL file manager."""
    copy_src = '11111'
    move_src = '22222'
    past_ = '33333'

    def __init__(self, device, log_name):
        super(FileManagerTCL, self).__init__(device, log_name)
        self.company = "jrdcom" if self.isMILAN_GL else "tcl.tct"
        self.home_id = self.device(resourceId="com.%s.filemanager:id/phone_storage_container" % self.company)
        self.past_btn = self.device(resourceId="com.%s.filemanager:id/floating_action_button" % self.company,
                                    description="Paste")
    
    def enter(self):
        """
        enter file manager
        :return: 
        """
        self.logger.info("enter file manager")
        if self.is_file_home():
            self.logger.info("file manager already opened")
            return True

        self.start_app('File Manager')
        return self.is_file_home()

    def enter_internal_storage_list(self):
        """
        enter storage list activity
        :return:
        """
        self.logger.info("enter storage list")
        assert self.is_file_home()
        self.home_id.click.wait()
        self.device(scrollable=True).scroll.vert.toBeginning(steps=100, max_swipes=100)
        self.device.wait.idle()
        return self.is_storage_list()

    def is_storage_list(self):
        """
        if it is storage list activity,
        all copy/move/past/del actions will perform in this activity
        :return:
        """
        if self.device(text="Internal storage", resourceId="com.%s.filemanager:id/path_text" % self.company).exists:
            return True
        else:
            return False

    def is_file_home(self):
        """
        if it is file manager home activity
        :return:
        """
        if self.home_id.wait.exists(timeout=2000):
            return True
        else:
            return False

    def back_to_storage_top(self):
        """
        back to the top of storage list
        :return:
        """
        if self.is_storage_list():
            return True
        try:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=100, max_swipes=100)
        except Exception as e:
            print e
            pass

        return self.is_storage_list()

    def is_folder_exist(self, folder):
        """
        judge folder exists or not
        :param folder:
        :return:
        """
        if self.device(text=folder).wait.exists(timeout=1000):
            self.logger.info("{} exists".format(folder))
            return True
        else:
            self.logger.info("{} NOT exists".format(folder))
            return False

    def create_folder(self, folder_name):
        """
        create folder via given name
        :param folder_name:
        :return:
        """
        self.logger.info("create folder")
        assert self.back_to_filemanager(), 'can not back to top storage list'
        self.device(resourceId="com.%s.filemanager:id/more_btn" % self.company).click()
        self.device.wait.idle()
        self.device(text="Create folder").click()
        self.device.wait.idle()

        self.device(text="Folder name").set_text(folder_name)
        self.device.wait.idle()
        if self.device(text="CREAT").exists:
            self.device (text="CREAT").click()
        else:
            self.click_text_CREATE()

        if self.device(text=folder_name).wait.exists(timeout=3000):
            self.logger.info("{} created".format(folder_name))
            return True
        else:
            self.logger.error("******* create {} failed ******".format(folder_name))
            return False

    def copy_past(self, src_folder=copy_src, past_folder=past_):
        """
        perform copy and past action
        :param src_folder:
        :param past_folder:
        :return:
        """
        self.logger.info("copy and past")
        assert self.back_to_filemanager(), 'can not back to top storage list'

        # create folders if needed
        self.create_folders_if_need(src_folder, past_folder)

        # copy
        self._copy(src_folder)

        # past
        self._past(past_folder)

        return True

    def move_past(self, src_folder=move_src, past_folder=past_):
        """
        perform move past action
        :param src_folder:
        :param past_folder:
        :return:
        """
        self.logger.info("move and past")
        assert self.back_to_filemanager(), 'can not back to top storage list'

        # create folders if needed
        self.create_folders_if_need(src_folder, past_folder)

        # copy
        self._move(src_folder)

        # past
        self._past(past_folder)

        return True

    def create_folders_if_need(self, *folders):
        """
        create folder if the folder not exist
        :param folders:
        :return:
        """
        for folder in folders:
            if not self.is_folder_exist(folder):
                self.create_folder(folder)

        # scroll to beginning to show all folders
        self.device.delay()
        self.device(scrollable=True).scroll.vert.toBeginning(steps=100, max_swipes=100)

    def enter_folder(self, folder_name):
        """
        enter a folder
        :param folder_name:
        :return:
        """
        self.device(text=folder_name).click()
        self.device.wait.idle()

    def _copy(self, src):
        self.device(text=src).long_click()
        self._click_more_options()
        self._perform_action('Copy')

        # verify
        assert self.past_btn.wait.exists(timeout=3000)

    def _move(self, src):
        self.device(text=src).long_click()
        self._click_more_options()
        self._perform_action('Move')

        # verify
        assert self.past_btn.wait.exists(timeout=3000)

    def _past(self, src):
        self.enter_folder(src)
        self.past_btn.click()

        # verify
        assert not self.past_btn.wait.exists(timeout=1000)

    def _del(self, src):
        self.device(textStartsWith=src).long_click()
        # self._click_more_options()
        # self._perform_action ('Delete')
        if self.device(description="Delete").exists:
            self.device (description="Delete").click()
        else:
            self._click_and_log(567, 89)
        self.device.wait.idle()
        if self.device(resourceId="android:id/button1",text="DELETE").exists:
            self.device (resourceId="android:id/button1", text="DELETE").click()
        else:
            self.click_text_DELETE ()
        # self.device(textMatches="DELETE|Delete", resourceId="android:id/button1").click()
        self.device.wait.idle()

    def _click_more_options(self):
        """
        click move options menu
        :return:
        """
        self.device(resourceId="com.%s.filemanager:id/more_btn" % self.company).click()
        self.device.wait.idle()

    def _perform_action(self, act_name):
        """
        click one option
        :param act_name:
        :return:
        """
        self.device(text=act_name).click()
        self.device.wait.idle()

    def del_folders(self):
        """
        delete all folders with name starts with self.copy_src, self.move_src, self.past_
        :return:
        """
        assert self.back_to_filemanager(), 'can not back to top storage list'
        folders = [self.copy_src, self.move_src, self.past_]
        for i in range(10):
            for folder in folders:
                if self.device(textStartsWith=folder).exists:
                    self._del(folder)

        # verify
        if self.device(textStartsWith=self.past_).exists:
            return False
        return True

    def back_to_filemanager(self):
        """
        back to file manager storage list activity
        :param param:
        :return:
        """
        if self.is_storage_list():
            return True
        for i in range(10):  # 10次机会
            if self.is_storage_list():
                break
            self.device.press.back()
            self.device.wait.idle()
        else:   # 可能已经到主屏了……
            self.enter()
            self.enter_internal_storage_list()

        # verify
        if self.is_storage_list():
            return True
        return False


if __name__ == '__main__':
    # device_id = get_connected_device()
    a = FileManagerTCL('1c87155b', "File")
    a.copy_past()
