#Create by chengkun.yue

from lib.common import Common
import random, string
filemanagerActivity = "com.jrdcom.filemanager/.activity.FileBrowserActivity"
setting_app_package='com.android.settings'
setting_app_activity='.Settings'

class FileManager(Common):
    def __init__(self, device, log_name="FILEMANAGER"):
        Common.__init__(self, device, log_name)
    
    def enterSettings(self):
        self._logger.debug('enter settings')
        self._device.start_activity(setting_app_package,setting_app_activity)
        self._device.delay(2)
        if self._device(textContains="Search settings").exists:
            self._logger.debug("enter Settings successful")
            return True
        self._logger.debug("enter Settings fail")
        return False
    
    def enterSubSetting(self, titleName):
        self.enterSettings()
        #listItem.child_by_text(titleName, text =titleName).click.wait()
        self._device.delay(2)
        if titleName=="SIM cards" or titleName=="Data usage":
            self._device(text ="Network & internet").click.wait()
            self._device(text =titleName).click.wait()
            if self._device(text="Preferred SIM for").exists:
                self._logger.info("Enter the %s successful" % titleName)
                return True
            if self._device(text="Cellular data").exists:
                self._logger.info("Enter the %s successful" % titleName)
                return True
        else:
            listItem = self._device(scrollable=True)
            if listItem.scroll.vert.to(text =titleName):
                self._device(text =titleName).click.wait()
        if self._device(description="Navigate up").exists:
            self._logger.info("Enter the %s successful" % titleName)
            return True
        self._logger.info("Enter the %s fail!" % titleName)
        return False
    
    def enterStorage(self, _store="Internal storage"):
        self._logger.info("Enter the %s" % _store)
        self.enterSubSetting("Storage")
        if _store.lower() == "internal storage":
            self._device(text ="Internal shared storage").click.wait()
        else:
            storeItem = self._device(resourceId="com.jrdcom.filemanager:id/sd_name")
            storeItem.click()
        self._device.delay(3)
        if self._device(text ="Storage").exists:
            self._logger.info("Enter the %s successful" % _store)
            return True
        self._logger.warning("Enter the %s fail!" % _store)
        return False
    
    def backToFileManager(self):
        for _ in range(5):
            if self._device(text="File Manager", resourceId="com.jrdcom.filemanager:id/path_text").exists:
                break
            self._device.press("back")
            self._device.delay(1)
        else:
            self.backToHome()
            self._device.start_activity(filemanagerActivity)
            self._device.delay(2)
            
    def enterFolder(self, _store="Internal storage", folderName="APK"):
        self._logger.info('Enter %s, Folder: %s' %(_store, folderName))
        if self._device(text='GOT IT').exists:
            self._device(text='GOT IT').click.wait()
            self._device.delay(1) 
        if self.enterStorage(_store):
            listItem = self._device(className="android.support.v7.widget.RecyclerView")
            listItem.scroll.vert.to(text="Files")
            self._device(text="Files").click.wait()
            listItem_2=self._device(className="android.support.v7.widget.RecyclerView")
            if not listItem_2.scroll.vert.to(text=folderName):
                self._logger.info('No Folder: %s' % folderName)
                return False
            folderItem = self._device(text=folderName)
            folderItem.click.wait()
            self._device.delay(2)
    
    def deleteFolder(self, folderName=""):
        old_num = self.get_file_num("/storage/emulated/0", "\n")+self.get_file_num("/storage/sdcard1", "\n")
        listItem = self._device(className="android.support.v7.widget.RecyclerView")
        if not listItem.scroll.vert.to(text=folderName):
            return True
        folderItem = self._device(text=folderName)
        folderItem.long_touch()
        self._device.delay(1)
        delItem = self._device(resourceId='com.jrdcom.filemanager:id/delete_btn')
        if delItem.wait.exists():
            delItem.click()
            self._device.delay(2)
            self._device(resourceId="android:id/button1").click()
            self._device.delay(2)
        new_num = self.get_file_num("/storage/emulated/0", "\n")+self.get_file_num("/storage/sdcard1", "\n")
        if new_num == old_num-1:
            return True
        return False
    
    def createNestFolder(self, _store="Phone Storage"):
        self._logger.info("Create nest folders")
        if self.enterStorage(_store):
            self.deleteFolder("test1")
            flag = True
            for i in range(10):
                self.selectOption("Create folder")
                folderName = "test%s"%(i+1)
                self._device(resourceId="com.jrdcom.filemanager:id/edit_text").set_text(folderName)
                self._device.delay(1)
                self._device(resourceId="android:id/button1").click.wait()
                self._device.delay(1)
                listItem = self._device(className="android.widget.ListView")
                folderItem = listItem.child_by_text(folderName, text=folderName)
                flag &= folderItem.exists
                if not flag:
                    break
                folderItem.click()
                self._device.delay(2)
            navBar = self._device(resourceId="com.jrdcom.filemanager:id/listview")
            navBar.scroll.horiz.toBeginning(steps=5)
            self._device.delay(1)
            if _store.lower() == "phone storage":
                _store = "Phone"
            if self._device(textMatches="(?i)"+_store).exists:
                self._device(textMatches="(?i)"+_store).click()
                self._device.delay(2)
                if self.deleteFolder("test1"):
                    return flag
        return False
    
    def selectOption(self, _option):
        self._device(resourceId="com.jrdcom.filemanager:id/more_btn").click.wait()
        self._device.delay(1)
        self._device(text=_option).click.wait()
        self._device.delay(1)
    
    def createAndDeleteFolder(self, _store="Phone Storage"):
        self._logger.info("Create new folder and delete")
        if self.enterStorage(_store):
            old_num = self.get_file_num("/storage/emulated/0", "\n")+self.get_file_num("/storage/sdcard1", "\n")
            createFlag = False
            self.selectOption("Create folder")
            name = "".join(random.sample(string.ascii_letters, 4))
            self._device(resourceId="com.jrdcom.filemanager:id/edit_text").set_text(name)
            self._device.delay(1)
            self._device(resourceId="android:id/button1").click()
            self._device.delay(2)
            new_num = self.get_file_num("/storage/emulated/0", "\n")+self.get_file_num("/storage/sdcard1", "\n")
            if old_num < new_num:
                self._logger.info("Create folder success")
                createFlag = True
            if createFlag and self.deleteFolder(name):
                return True
            return False
        
    def renameFile(self, _store="Phone Storage"):
        self._logger.info("Rename file")        
        if self.enterStorage(_store):
            name = "test_rename"
            for _ in range(2):
                try:
                    listItem = self._device(className="android.widget.ListView")
                    if not listItem.scroll.to(text=name):
                        self._device.press("back")
                        self._device.delay(1)
                        self.enterStorage(_store)
                        if not listItem.scroll.to(text=name):
                            self._logger.warning("the %s file don't exists!"%name)
                            return False
                    self._device(text=name).long_touch()
                    self._device.delay(1)
                    self.selectOption("Rename")
                    self._device.delay(2)
                    if name == "test_rename":
                        name = "".join(random.sample(string.ascii_letters*10, 255))
                    else:
                        name = "test_rename"
                    self._device.delay(2)
                    editItem = self._device(resourceId="com.jrdcom.filemanager:id/edit_text")
                    for _ in range(10):
                        if not editItem.getText():
                            break
                        editItem.clear_text()
                    editItem.set_text(name)
                    self._device.delay(1)
                    self._device(resourceId="android:id/button1").click()
                    self._device.delay(2)
                    if self._device.isKeyboardShown():
                        self._device.press("back")
                        self._device.delay(1)
                except Exception:
                    return False
            return True
        return False
    
    def cutFile(self, _store="Phone Storage"):
        self._logger.info("Cut file")        
        if self.enterStorage(_store):
            try:
                listItem = self._device(className="android.widget.ListView")
                if not listItem.scroll.vert.to(textStartsWith="cutFile"):
                    self._logger.warning("the cutFile file don't exists")
                    return False
                fileItem = self._device(textStartsWith="cutFile")
                fileItem.long_touch()
                self._device.delay(1)
                self.selectOption("Cut")
                listItem.fling.toBeginning(max_swipes=2)
                listItem.child_by_text("test", text="test").click()
                self._device.delay(2)
                self.selectOption("Paste")
                if fileItem.wait.exists(timeout=5000):
                    fileItem.long_touch()
                    self._device.delay(1)
                self.selectOption("Cut")
                if _store.lower() == "phone storage":
                    _store = "phone"
                self._device(textMatches="(?i)"+_store, resourceId="com.jrdcom.filemanager:id/horizontallist_item_path").click()
                self._device.delay(1)
                self.selectOption("Paste")
                return True
            except Exception:
                return False
        return False
                
if __name__ == "__main__":
    import common
    d = common.Device("f958c692")
    fm = FileManager(d)
    fm.renameFile()
