#_*_ coding: UTF-8 _*_
from lib import common
import traceback
import sys,random
import subprocess
from lib.common import Common
from lib.fileManager import FileManager

setting_app_package='com.android.settings'
setting_app_activity='.Settings'

d=["4 wide by 5 high","2 wide by 3 high","2 wide by 2 high","4 wide by 3 high"]
class Launcher(Common):
    def __init__(self, device, log_name="LAUNCHER"):
        super(Launcher, self).__init__(device, log_name)
        
    def clearLauncher(self):
        self._logger.info("Clear launcher!")
        self._device.adb_command("shell pm clear com.tcl.android.launcher")
        self._device.delay(5)
        self._device.press('back')
        self._device.press ('back')
        self._device.press ('back')
        self._device.press ('home')
        self._device.delay(3)
        for _ in range(10):
            if self._device(text="ALLOW").exists:
                self._device(text="ALLOW").click()
                self._device.delay(1)
            if self._device(text="Finish").exists:
                self._device(text="Finish").click()
            self._device.delay(1) 
            if self._device(resourceId="com.tcl.android.launcher:id/layout").exists: 
                break    
        self.backToHome()
        
    def backToHome(self):
        self._logger.info('back to home')
        self._device.press('home')
        self._device.delay(1)
    
    def setWallpaper(self, time=1):
        try:
            for _ in range(5):
                self._device.press("menu")
                self._device.delay(2)
                if self._device(text="Wallpapers").exists:
                    break
            if self._device(text='GOT IT').exists:
                self._device(text='GOT IT').click.wait()
                self._device.delay(1)
            self._device(text="Wallpapers").click.wait()
            self._device.delay(1)
            if time%2 != 0:
                for _ in range(3):
                    if self._device(text = 'My photos').exists:
                        self._device(text = 'My photos').click.wait()
                        self._device.delay(1)
                        break
                    else:
                        self._device.swipe(368,1266,368,550,8)
                while self._device(text="ALLOW").exists:
                    self._device(text="ALLOW").click()
                if self._device(text='wallpaper').exists:
                    self._device(text='wallpaper').click()
                    self._device.delay(1)
                if self._device(resourceId='com.tclhz.gallery:id/comments_image_item').exists:
                    self._device(resourceId='com.tclhz.gallery:id/comments_image_item').click()
                    self._device.delay(1)
                if self._device(text='Pictures').exists:
                    self._device(text='Pictures').click()
                    self._device.delay(1)
                _index = random.choice(range(1,6))
                if self._device(text="enterPhoto").exists:
                    self._device (text="enterPhoto").click()
                    self._device.delay (2)
                self._device(instance= _index,resourceId = "com.tclhz.gallery:id/comments_image_item").click()
                self._device.delay(1)    
            else:
                self._device(resourceId="com.tcl.android.launcher:id/wallpaper_thumbnails_item").click.wait()
                if self._device(resourceId="com.tcl.android.launcher:id/wallpaper_switch_prompt_text").exists:
                    self._device(resourceId="com.tcl.android.launcher:id/wallpaper_switch_prompt_text").click.wait()
#                 for _ in range(3):
#                     if self._device(resourceId="com.tct.launcher:id/wallpaper_list").exists:
#                         self._device(resourceId="com.tct.launcher:id/wallpaper_list").click.wait()
#                         self._device.delay(1)
#                         break
#                     else:
#                         self._device.swipe(368,1266,368,550,8)
#                 if self._device(textContains="JUST"):
#                     self._device(textContains="JUST").click.wait()
#                 _index = random.choice(range(1,2))
#                 self._device(instance= _index,resourceId = "com.google.android.apps.photosgo:id/single_photo").click()
#                 self._device.delay(1)
#             if self._device(resourceId="com.tct.launcher:id/wallpaper_image").exists:
#                 self._device(resourceId="com.tct.launcher:id/wallpaper_image").click.wait()
            if self._device(text="Done").exists:
                self._device(text="Done").click.wait()
                self._device.delay(1)
            self._device.press('home')
            self._device.delay(2)
            if self._device(resourceId="com.tcl.android.launcher:id/layout").exists:
                return True
            return False
        except Exception:
            common.log_traceback(traceback.format_exc())
            return False
        finally:
            self.backToHome()
            
    def enterFolder(self, _store="Files", folderName="APK"):
        self._logger.info('Enter %s, Folder: %s' %(_store, folderName))
        if self._device(text='GOT IT').exists:
            self._device(text='GOT IT').click.wait()
            self._device.delay(1) 
        if self.enterStorage(_store):
            listItem = self._device(resourceId="com.android.settings:id/recycler_view")
            listItem.scroll.vert.to(text="Files")
            self._device(text="Files").click.wait()
            listItem_2=self._device(resourceId="com.android.documentsui:id/dir_list")
            if not listItem_2.scroll.vert.to(text=folderName):
                self._logger.info('No Folder: %s' % folderName)
                return False
            folderItem = self._device(text=folderName)
            folderItem.click.wait()
            self._device.delay(2)
    
    def enterStorage(self, _store="Files"):
        self._logger.info("Enter the %s" % _store)
        self.enterSubSetting("Storage")
        self._device.delay(2)
        if _store == "Files":
            if self._device(text =_store).exists:
                self._device(text =_store).click.wait()
        self._device.delay(3)
        if self._device(text ="Alarms").exists:
            self._logger.info("Enter the %s successful" % _store)
            return True
        self._logger.warning("Enter the %s fail!" % _store)
        return False
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
    
    def enterNavMenu(self):
        for _ in range(3):
            self._device.press("home")
            self._device.delay(1)
            self._device.swipe(360,1000,360,200,20)
            self._device.delay(1)
            if self._device(resourceId="com.tcl.android.launcher:id/search_box_input").exists:
                self._logger.info("Enter Navmenu successfully!")
                return True
        self._logger.info("Enter Navmenu fail!")
        return False 
        
    def backToMenu(self):
        for _ in range(3):
            if self._device(resourceId="com.android.launcher3:id/apps_list_view").exists:
                break
            self._device.press("back")
            self._device.delay(1)
        else:
            self._device.press("home")
            self._device.delay(2)
            self._device(descriptionMatches="(?i)Apps list").click()
            self._device.delay(2) 
            
    def changeIconOnNavMenu(self):
        if self._device(resourceId="com.tcl.android.launcher:id/all_apps_sort_order_settings").exists:
            self._device(resourceId="com.tcl.android.launcher:id/all_apps_sort_order_settings").click.wait()
        if self._device(text="By name").isChecked():
            self._device.press('back')
        else:
            self._device(text="By name").click.wait()
        self._device.delay(1)
                
    def createFolder(self):
        self._logger.info('Create Folder on home screen')
        self.enterNavMenu()
        self.changeIconOnNavMenu()
        for i in range(4):
            _index = 0
            for j in range(10):
                _index += 1
                self._logger.info('Drag %s icon to home screen......' % (i*10+j+1))
                self.enterNavMenu()
                item = self._device(resourceId='com.tcl.android.launcher:id/icon', index=_index)
                item.drag.to(x=441, y=963,steps=20)
        if self._device(description="Folder: Unnamed Folder").exists:
            self._device(description="Folder: Unnamed Folder").click()
            self._device.delay(1)
            self._device.press("home")
            return True
        return False

    
    def deleteFolder(self):
        self._logger.info('Delete Folder')
        for _ in range(3):
            folder_item = self._device(description="Folder: Unnamed Folder")
            if folder_item.exists:
                folder_item.drag.to(x=619, y=25, steps=40)
                self._device.delay(2)
            if not folder_item.exists:
                self._logger.info('Delete Folder successfully!')
                return True
        self._logger.info('Delete Folder fail!')
        return False
        
    def openFolder(self):
        self._logger.info('Open Folder')
        if self._device(text='GOT IT').exists:
            self._device(text='GOT IT').click.wait()
            self._device.delay(1)
        for _ in range(3):
            folder_item = self._device(description="Folder: Unnamed Folder")
            if folder_item.exists:
                folder_item.click.wait()
                self._device.delay(2)
            if self._device(text='Unnamed Folder').exists:
                self._logger.info('Open Folder successfully!')
                return True
        if self._device(text='Unnamed Folder').exists:
            return True
        return False
    
    def closeFolder(self):
        self._logger.info('Close Folder')       
        if self._device(resourceId='com.tcl.android.launcher:id/folder_content_wrapper').exists:
            self._device.press('home')
            self._device.press('home')
            self._device.delay(2)
            return True
        self._device.press('home')
        return False
    
    def removeApp(self, appName):
        self._logger.info('Remove App on home screen: '+appName)
#         apps=['Secure Net Wi-Fi','Accessories','Amap ','Fill','Outlook','Keep','Mein Vodafone','Tips','Vodafone MyTone','Cardboards','Feedback']       
#         if appName in apps:
        if self._device(description=appName).exists:
            self._device(description=appName).drag.to(x=570, y=32, steps=40)   
            self._device.delay(1)
#         else:
#             if self._device(description=appName).exists:
#                 self._device(description=appName).drag.to(x=240,y=51)
#                 self._device.delay(1)
#             if self._device(text=appName).exists:
#                 self._device(text=appName).drag.to(x=395,y=305,steps=40)  
#                 self._device.delay(1) 
    
    def getPageCount(self):
        if self._device(text='GOT IT').exists:
            self._device(text='GOT IT').click.wait()
            self._device.delay(1)
        return 2
#         if self._device(resourceId='com.android.launcher:id/page_indicator').exists:
#             return self._device(resourceId='com.android.launcher:id/page_indicator').getChildCount()
    
    def clearAllShortcut(self, pageCount=10):
        for loop in range(pageCount):
            self.backToHome()
            self._device(className='android.view.View', index=0).swipe.left()
            self._device.delay(2)
            if self._device(resourceId="com.tcl.android.launcher:id/qsb_widget").exists:
                self._logger.info("No shortcut on other page!")
                return True
            self._logger.info('Clear all shortcut for page: %s' % (loop+1))
            count = self._device(className='android.view.ViewGroup', index=1).getChildCount()
            print(count)
            for _ in range(count):
                lstView = self._device(className='android.view.ViewGroup', index=1)
                des=lstView.child(index=0).getContentDescription()
                print(des)
                self._device.delay(1)
                self.removeApp(des)
        self._device(className='android.view.View', index=0).swipe.left()
        self._device.delay(2)
        if not self._device(resourceId="com.tcl.android.launcher:id/qsb_widget").exists:
            self._logger.info("Fail to clear all other page!")
            return False
#         if self._device(className='android.view.ViewGroup', index=0).getChildCount() != 0:
#             self._logger.info('Cannot clear page!')
#             return False
                
    def addShortcut(self, pageCount=5):
        self.enterNavMenu()
        self.changeIconOnNavMenu()
        self.backToHome()
        for loop in range(pageCount):
            self._logger.info('Add Shortcut for Page: %s' % (loop+1))
            for app in range(24):
                    self._device.swipe(360,1000,360,200,20)
                    self._device.delay(1)
                    if app>=22:
                        item = self._device(resourceId='com.tcl.android.launcher:id/icon', instance=5)
                    else:
                        item = self._device(resourceId='com.tcl.android.launcher:id/icon', instance=app+1)
                    if app == 0:
                        item.drag.to(x=700, y=166,steps=20)#y:first row ordinate
                        self._device.delay(1)
                    else:
                        try:    
                            item.drag.to(x=99+(app//6)*174, y=166+(app%6)*180, steps=20)
                            '''
                            x=a+(app//b)*c,y=d+(app%b)*e
                            a:first column abscissa
                            b:first column icon number
                            c:one row adjacent icon abscissa difference
                            d:first row ordinate
                            e:one column adjacent icon ordinate difference
                            '''
                            self._device.delay(1)
                            if self._device(text="App info").exists:
                                self._device.press('home')
                                self._device.delay(1)
                        except Exception:
                                common.log_traceback(traceback.format_exc())
                                self.save_fail_img()  
            count=self._device(className='android.widget.TextView').count
            if count < 20:
                self._logger.info('Add Shortcut for Page: %s fail'  % (loop+1))
                return False
        self._logger.info('Add Shortcut successfully!')
        return True
    
    def prepareIdle(self):
        self._logger.info('Prepare Idle Screen')
        self.backToHome()
        for _ in range(4):
            self._device.swipe(360,1000,360,200,20)
            self._device.delay(1)
            item = self._device(resourceId='com.tcl.android.launcher:id/icon', index=1)
            item.drag.to(x=700, y=200,steps=20)
            self._device.delay(1)
        self._device.press('home')
        
    def changeIdle(self):
        self._logger.info('Change Idle Screen')
        self.backToHome()
        self._device.press("menu")
        self._device.delay(2)
        for _ in range(4):
            self._device(resourceId='com.tcl.android.launcher:id/workspace').swipe.left()
        self._device.delay(1)
        self._device(resourceId='com.tcl.android.launcher:id/workspace').drag.to(-500,1000,steps=50)   
        self._device.delay(1)
        self._device.press('home')
        return True
                
    def addDynamicApp(self, appName):
        self._logger.info('Add Dynamic App to home screen: '+appName)
        self.enterNavMenu()
        item = self._device(text=appName)
        item.drag.to(x=360, y=720,steps=10)
        if self._device(text=appName).exists:
            return True
        return False
            
    def addWidget(self, pageCount = 5):
        
        for loop in range(pageCount):
            self._logger.info('Add Widget for Page: %s' % (loop+1))
            self._device.press('menu')
            self._device.delay(2)
            self._device(text="Shortcuts").click.wait()
            self._device.delay(1)
            listView = self._device(resourceId='com.tcl.android.launcher:id/widgets_list_view')
            if listView.exists:
#                     if loop > 0 and loop1 == 0:
#                         self._device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=480,y=399.5,steps=40)
#                         self._device.delay(2)
#                     elif loop == 0 and loop1 == 0:
#                         self._device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=320,y=634.5,steps=40)
#                         self._device.delay(2)
#                     else:
                self._device(resourceId='com.tcl.android.launcher:id/widget_name', text = "Lock").drag.to(x=360,y=720,steps=40)
                self._device.delay(2)
#                     self._device(resourceId='com.android.launcher3:id/widget_preview', instance = 2).drag.to(x=380,y=399.5,steps=40)
#                     self._device.delay(2)
        lstView = self._device(description='Lock') 
        if lstView.exists:
            self._logger.debug("Add widget successfully!")
            return True
        self._logger.debug("Add widget fail!")
        return False
#                 if listView.exists:
#                     if loop > 0 and loop1 == 0: 
#                         self._device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=1420,y=800,steps=40)
#                         self._device.delay(2)
#                         self._device(resourceId='com.android.launcher3:id/workspace').swipe.left()
#                         self._device.delay(1)
#                     elif loop == 0 and loop1 == 0:
#                         self._device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=480,y=980,steps=40)
#                         self._device.delay(2)
#                     else:
#                         self._device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=750,y=1080,steps=40)
#                         self._device.delay(2)                        
#             lstView = self._device(className='android.view.ViewGroup', instance=1) 
#             flag &= (lstView.getChildCount() == 2)
#         if flag:
#             return True
#         return False
            
    def readFile(self, name='apk.txt'):  
        fi = open(sys.path[0]+'\\lib\\'+name, 'r')
        try:
            return fi.readlines()                 
        finally:
            fi.close()
                           
            
    def uninstallAPK(self):
        lines = self.readFile('package_milan.txt')
        for line in lines:
            self._logger.info('Uninstall APK: %s' % line)
            subp = subprocess.Popen('adb uninstall %s' % line, shell=True)
            subp.communicate()
        
            
    def installAPK(self, number = 28):
        lines = self.readFile()
        flag = True
        if not self._device (text="APK").exists:
            self.enterStorage()
            self._device.delay(2)
            if self._device (text="APK").exists:
                self._device (text="APK").click ()
        else:
            self._device (text="APK").click ()
            self._device.delay (2)
        self._device.delay (2)
        listView = self._device (resourceId="com.google.android.documentsui:id/dir_list")
        for loop in range(number):
            if listView.exists:
                self._logger.info('Install APK: %s' % lines[loop].strip())
                self._device.delay(1)
                if not listView.scroll.vert.to(text=lines[loop].strip()):
                    self._logger.warning('APK named %s not exists!' % lines[loop].strip())
                    continue
                if  self._device(text = lines[loop].strip()).exists:
                    self._device(text = lines[loop].strip()).click.wait()
                self._device.delay(2)
                if self._device(resourceId='android:id/button1',text='CONTINUE').exists:
                    self._device(resourceId='android:id/button1',text='CONTINUE').click.wait()
                    self._device.delay(1)
                if self._device(resourceId='com.android.packageinstaller:id/ok_button',text='NEXT').exists:
                    self._device(resourceId='com.android.packageinstaller:id/ok_button',text='NEXT').click.wait()
                    self._device.delay(1)
                if self._device(resourceId='com.android.packageinstaller:id/ok_button',text='Next').exists:
                    self._device(resourceId='com.android.packageinstaller:id/ok_button',text='Next').click.wait()
                    self._device.delay(1)
                if self._device(resourceId='com.android.packageinstaller:id/ok_button',text='INSTALL').exists:
                    self._device(resourceId='com.android.packageinstaller:id/ok_button',text='INSTALL').click.wait()
                    self._device.delay(1)
                if self._device(text='INSTALL').exists:
                    self._device(text='INSTALL').click.wait()
                self._device.delay(1)
                self._device(text='Installing…').wait.gone(timeout=120000)
                self._device.delay(1)
                item = self._device(text='App installed.')
                flag &= item.exists
                if item.exists:
                    self._device(text='DONE').click.wait()
                    self._device.delay(2)
            else:
                self._logger.warning('No APK in folder !')
                return False
        if flag:
            return True
        return False

                
if __name__ == "__main__":
    d = common.Device("501f6876")
#     d.press("menu")
    #print d.get_current_packagename()
    l = Launcher(d)
    l.closeFolder()
    print("over")
#     l.changeIdle()
#     l.clearAllShortcut()
#     l.createFolder()
#     item = l._device(className='android.view.ViewGroup',index=1).getChildCount()
#     print(item)