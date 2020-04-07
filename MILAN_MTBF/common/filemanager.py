# -*- coding: UTF-8 -*-
"""Telephony library for scripts.
"""
from common import *
from ui_parser import UIParser


class FileManager(Common):
    """Provide common functions for scripts, such as launching activity."""

    def enter(self, path="Files"):
        self.logger.debug("Enter FileManager Of Path %s " % path)
        if self.device(text=path).exists:
            self.device(text=path).click()
            self.device.delay(2)
        if self.device(text=path, resourceId="com.jrdcom.filemanager.bb:id/path_text").exists:
            self.logger.debug("Enter FileManager Of Path %s success!!!" % path)
            return True
        self.start_app("Files")
        self.device.delay(2)
        if not self.device(text="Files").exists:
            self.back_to_filemanager()
        if self.device(text=path).exists:
            self.device(text=path).click()
            self.device.delay(1)
        else:
            self.logger.debug(path)
        if self.device(text=path, resourceId="com.jrdcom.filemanager.bb:id/path_text").wait.exists(timeout=1000):
            self.logger.debug("Enter FileManager Of Path %s success!!!" % path)
            return True
        else:
            self.logger.debug("Enter FileManager Of Path %s fail!!!" % path)
            self.save_fail_img()
            return False

    def back_to_filemanager(self, path=None):
        self.logger.debug('back to filemanager')
        mark = "Files" if path is None else path
        home_id = self.device(text=mark, resourceId="com.jrdcom.filemanager.bb:id/path_text")
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
        for loop in range(5):
            if home_id.wait.exists(timeout=2000):
                return True

            # sometimes device will back to home screen, add security code
            # if self.device(description="All Items").wait.exists(timeout=1000) or self.device(description="Apps").exists:
            #     self.enter()
            #     continue
            self.device.press.back()
            self.device.delay(1)

        self.back_to_home()
        if self.enter(path):
            self.logger.debug('back to filemanager success')
            return True
        self.save_fail_img()
        return False

    def checkRename(self, path):
        self.logger.debug("check rename folder")
        self.enter(path)
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
            self.device(scrollable=True).scroll.vert.to(text="test_rename")
        if not self.device(text="test_rename").wait.exists(timeout=2000):
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
            self.device(scrollable=True).scroll.vert.to(textStartsWith="Auto")
            if self.device(textStartsWith="Auto").wait.exists(timeout=2000):
                name1 = self.device(textStartsWith="Auto").get_text()
                if not self._rename_file(name1, "test_rename"):
                    self.logger.debug("check rename fail!!!")
                    return False
            else:
                self.logger.debug("rename folder or Auto file doesn't exists!!!")
                return False
        return True

    def search_cutfile(self, name, path="back"):
        self.logger.info("search cut file")
        if not self.device(text=self.appconfig("cut_paste_folder", "FileManager")).exists:
            self.device(scrollable=True).scroll.vert.to(text=self.appconfig("cut_paste_folder", "FileManager"))
        self.device(text=self.appconfig("cut_paste_folder", "FileManager")).click()
        if self.device(text=name).wait.exists(timeout=2000):
            self.cut_file(name)
            self.paste_file(name, path)

    def cut_file(self, name, path=None):
        self.logger.info("cut the file %s" % name)
        if not path is None:
            if not self.enter(path):
                return False
        if not self.device(text=name).exists:
            self.device(scrollable=True).scroll.vert.to(text=name)
        if not self.device(text=name).exists:
            self.logger.info("file %s not exists" % name)
            self.search_cutfile(name)
        if self.device(scrollable=True):
            self.device(scrollable=True).scroll.vert.to(text=name)
        cut = [
            {"id": {"text": name}, "action": {"type": "long_click"}},
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/fab_expand_menu_button"}},
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/float_action_cut"}},
        ]
        UIParser.run(self, cut)
        self.device.delay(2)
        if self.device(description="Paste").wait.exists(timeout=5000):
            self.logger.debug("cut the file %s success" % name)
            return True
        else:
            self.cut_file_again(name)
            if self.device(description="Paste").wait.exists(timeout=5000):
                self.logger.debug("cut the file %s success" % name)
                return True
            else:
                self.logger.debug("cut the file %s failed" % name)
                self.save_fail_img()
                return False

    def cut_file_again(self, name, path=None):
        self.logger.info("cut the file %s" % name)
        if not path is None:
            if not self.enter(path):
                return False
        if not self.device(text=name).exists:
            self.device(scrollable=True).scroll.vert.to(text=name)
        if not self.device(text=name).exists:
            self.logger.info("file %s not exists" % name)
            self.search_cutfile(name)
        if self.device(scrollable=True):
            self.device(scrollable=True).scroll.vert.to(text=name)
        cut = [
            {"id": {"text": name}, "action": {"type": "long_click"}},
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/fab_expand_menu_button"}},
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/float_action_cut"}},
        ]
        UIParser.run(self, cut)
        self.device.delay(2)

    def paste_file(self, name, path=None):
        if not path is None:
            self.logger.info("paste the %s to path" % name)
            self.device.press.back()
            self.device.delay(2)
        else:
            self.logger.info("paste the %s to Test Folder" % name)
            if not self.device(text=self.appconfig("cut_paste_folder", "FileManager")).exists:
                self.device(scrollable=True).scroll.vert.to(text=self.appconfig("cut_paste_folder", "FileManager"))
                if not self.device(text=self.appconfig("cut_paste_folder", "FileManager")).exists:
                    self.create_folder(self.appconfig("cut_paste_folder", "FileManager"))
            self.device(text=self.appconfig("cut_paste_folder", "FileManager")).click()
            self.device.delay(2)
        self.device(resourceId="com.jrdcom.filemanager.bb:id/floating_action_button").click()
        if self.device(text=name).wait.exists(timeout=5000):
            self.logger.info("paste %s success" % name)
            return True
        else:
            self.logger.info("paste %s failed" % name)
            self.save_fail_img()
            return False

    def create_folder(self, name, path=None):
        if not path is None:
            if not self.enter(path):
                return False
        self.logger.debug("Create folder %s in %s storage." % (name, path))
        if not self.device(resourceId="com.jrdcom.filemanager.bb:id/more_btn").exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
        create = [
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/more_btn"}},
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/createfolder_item"}},
            {"id": {"text": "Folder name"}, "action": {"type": "set_text", "param": [name]}},
            {"id": {"resourceId": self.appconfig("id_button1", "FileManager")}},
        ]
        UIParser.run(self, create)
        self.device.delay(2)
        if self.device(text=name).exists:
            self.logger.debug("Create folder %s in %s storage success" % (name, path))
            return True
        self.device(scrollable=True).scroll.vert.to(text=name)
        if self.device(text=name).exists:
            self.logger.debug("Create folder %s in %s storage success" % (name, path))
            return True
        else:
            self.logger.debug("Create folder %s in %s storage failed" % (name, path))
            self.save_fail_img()
            return False

    def delete_folder(self, name, path=None):
        if not path is None:
            if not self.enter(path):
                return False
        self.logger.debug("Delete the folder %s" % name)
        if not self.device(text=name).exists:
            self.device(scrollable=True).scroll.vert.to(text=name)
        if self.device(text=name).exists:
            self.logger.info("folder %s exists" % name)
            delete = [
                {"id": {"text": name}, "action": {"type": "long_click"}},
                {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/fab_expand_menu_button"}},
                {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/float_action_delete"}},
                {"id": {"resourceId": "android:id/button1"}},
            ]
            UIParser.run(self, delete)
            self.device.delay(2)
            self.device(scrollable=True).scroll.vert.to(text=name)
            if not self.device(text=name).exists:
                self.logger.debug("Delete the folder %s success" % name)
                return True
            else:
                self.delete_folder_again(name)
                self.device.delay(2)
                self.device(scrollable=True).scroll.vert.to(text=name)
                if not self.device(text=name).exists:
                    self.logger.debug("Delete the folder %s success" % name)
                    return True
                else:
                    self.logger.debug("Delete the folder %s failed" % name)
                    self.save_fail_img()
                    return False
        else:
            self.logger.info("folder %s not exists" % name)
            self.save_fail_img()
            return False

    def delete_folder_again(self, name, path=None):
        if not path is None:
            if not self.enter(path):
                return False
        self.logger.debug("Delete the folder %s" % name)
        if not self.device(text=name).exists:
            self.device(scrollable=True).scroll.vert.to(text=name)
        if self.device(text=name).exists:
            self.logger.info("folder %s exists" % name)
            delete = [
                {"id": {"text": name}, "action": {"type": "long_click"}},
                {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/fab_expand_menu_button"}},
                {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/float_action_delete"}},
                {"id": {"resourceId": "android:id/button1"}},
            ]
            UIParser.run(self, delete)

    def create_multifolder(self, name, path):
        self.logger.info("Create multi folders 10 times in %s" % path)
        if self.create_folder(name, path):
            self.logger.debug("create folder " + name + " 1 times.")
            self.device(scrollable=True).scroll.vert.to(text=name)
            self.device(text=name).click()
            self.device.delay(2)
            for index in range(10):
                if self.create_folder(name):
                    self.logger.debug("create folder " + name + " " + str(index + 2) + " times.")
                    self.device(text=name).click()
                    self.device.delay(2)
                else:
                    self.logger.warning("Cannot create %s folder!" % name)
                    self.save_fail_img()
                    return False
            self.logger.info("Create multi folders 10 times in %s success" % path)
            self.device(text="Home").click()
            self.enter(path)
            return True
        else:
            self.logger.info("Create multi folders 10 times in %s failed" % path)
            self.save_fail_img()
            return False

    def _rename_file(self, name1, name2, path=None):
        self.logger.info("rename the folder %s" % name1)
        if not path is None:
            if not self.enter(path):
                return False
        if not self.device(text=name1).exists:
            self.device(scrollable=True).scroll.vert.to(text=name1)
        if not self.device(text=name1).exists:
            self.create_folder(name1)
            self.device(scrollable=True).scroll.vert.to(text=name1)
        if self.device(text=name1).exists:
            rename = [
                {"id": {"text": name1}, "action": {"type": "long_click"}},
                {"id": {"resourceId": self.appconfig.id("id_more_btn", "FileManager")}},
                {"id": {"resourceId": self.appconfig.id("id_rename", "FileManager")}},
                {"id": {"resourceId": self.appconfig.id("id_edit_text", "FileManager")},
                 "action": {"type": "set_text", "param": [name2]}},
                {"id": {"text": "Rename", "resourceId": "android:id/button1"}}
            ]
            UIParser.run(self, rename)
            self.device.delay(2)
            if not self.device(text=name2).exists:
                self.device(scrollable=True).scroll.vert.to(text=name2)
            if self.device(text=name2).exists:
                self.logger.info("rename %s to %s success" % (name1, name2))
                return True
            else:
                self.logger.info("rename %s to %s failed" % (name1, name2))
                self.save_fail_img()
                return False
        else:
            self.logger.info("the folder %s not exists" % name1)
            self.save_fail_img()
            self.create_folder(name1)
            return False

    def copy_pre_file(self, name):
        self.logger.info("copy folder %s" % name)
        self.device(scrollable=True).scroll.vert.to(text=name)
        if not self.device(text=name).exists:
            self.create_folder(name)
        cut = [
            {"id": {"text": name}, "action": {"type": "long_click"}},
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/fab_expand_menu_button"}},
            {"id": {"resourceId": "com.jrdcom.filemanager.bb:id/float_action_copy"}},
        ]
        UIParser.run(self, cut)
        self.device.delay(2)
        if self.device(description="Paste").wait.exists(timeout=5000):
            self.logger.debug("copy the file %s success" % name)
            return True
        else:
            self.logger.debug("cut the file %s failed" % name)
            return False

    def create_paste_cut_delete_folder(self, name):
        self.logger.info("create parent、son folder, paste、cut %s folder, delete parent folder" % name)
        self.logger.info("create parent folder")
        if self.create_folder("parent"):
            self.device(text="parent").click.wait()
            self.logger.info("create son folder in parent")
            if self.create_folder("son"):
                self.device(text="son").click.wait()
                self.logger.info("paste the preset %s folder in son" % name)
                self.device(resourceId="com.jrdcom.filemanager.bb:id/floating_action_button").click()
                if self.device(text=name).wait.exists(timeout=5000):
                    self.logger.info("paste %s success" % name)
                    self.logger.info("cut %s to parent" % name)
                    if self.cut_file(name) and self.paste_file(name, "parent"):
                        self.logger.info("delete parent folder")
                        self.device.press.back()
                        return self.delete_folder("parent")
                    else:
                        return False
                else:
                    self.logger.info("paste %s failed" % name)
                    self.save_fail_img()
                    return False
            else:
                return False
        else:
            return False

    def clear_test_folder(self):
        test_folders = ['parent', 'son', 'test*']
        folder_path = 'sdcard/'
        test_folders = [folder_path + item for item in test_folders]
        cmd = 'rm -rf {{{}}}'.format(','.join(test_folders))
        self.logger.info(cmd)
        self.adb.shell(cmd)


if __name__ == '__main__':
    a = FileManager("2cdcda2b", "File")
    # a.create_del_folder(2)
    # a.create_del_multifolder("Phone", 2)
    # a.cut_paste_file("Phone",2)
    # a.rename_file( "Phone", 2)
    # a.rename_file( "SD", 2)
    a.cut_file("test_video.mp4")
    # a.create_del_multifolder("SD", 2)
