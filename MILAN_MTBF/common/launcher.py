#_*_ coding: UTF-8 _*_
import traceback
import sys
import random
import subprocess, random
from common import *


setting_app_package='com.android.settings'
setting_app_activity='.Settings'

d=["4 wide by 5 high","2 wide by 3 high","2 wide by 2 high","4 wide by 3 high"]
class Launcher(Common):
    def __init__(self, device, log_name="LAUNCHER"):
        super(Launcher, self).__init__(device, log_name)
        self.icon_container = self.device(className='android.view.ViewGroup', index=1, clickable=False)
        
    def clearLauncher(self):
        self.logger.info("Clear launcher!")
        self.adb.shell("shell pm clear com.tcl.android.launcher")
        # self.device.adb_command("shell pm clear com.tcl.android.launcher")
        self.device.delay(5)
        self.backToHome()
        
    def backToHome(self):
        self.logger.info('back to home')
        self.device.press('home')
        self.device.delay(1)
    
    def setWallpaper(self, time=1):
        try:
            self.device.press("menu")
            self.device.delay(2)
            if self.device(text='GOT IT').exists:
                self.device(text='GOT IT').click.wait()
                self.device.delay(1)
            self.device(text="Wallpapers").click.wait()
            self.device.delay(1)
            if time%2 != 0:
                for _ in range(3):
                    if self.device(text = 'My photos').exists:
                        self.device(text = 'My photos').click.wait()
                        self.device.delay(1)
                        break
                    else:
                        self.device.swipe(368,1266,368,550,8)
                if self.device(text="Gallery").wait.exists(timeout=500):
                    self.device(text='Gallery').click()
                    self.device.delay(timeout=1)
                    self.device(text='ALWAYS').click()

                if self.device(text='wallpaper').exists:       # 需要设置gallery默认打开方式
                    self.device(text='wallpaper').click()
                    self.device.delay(1)
                if self.device(resourceId='com.tclhz.gallery:id/comments_image_item').exists:
                    self.device(resourceId='com.tclhz.gallery:id/comments_image_item').click()
                    self.device.delay(1)
                    #listItem = self.device(resourceId='com.google.android.apps.photos:id/photo_container')
            else:
                self.device(resourceId="com.tcl.android.launcher:id/static_wallpapers_thumb").click()
#                 for _ in range(3):
#                     if self.device(resourceId="com.tct.launcher:id/wallpaper_list").exists:
#                         self.device(resourceId="com.tct.launcher:id/wallpaper_list").click.wait()
#                         self.device.delay(1)
#                         break
#                     else:
#                         self.device.swipe(368,1266,368,550,8)
#                 if self.device(textContains="JUST"):
#                     self.device(textContains="JUST").click.wait()
                _index = random.choice(range(1,7))
                self.device(instance= _index,resourceId = "com.tcl.android.launcher:id/thumbnail").click()
                self.device.delay(1)
#             if self.device(resourceId="com.tct.launcher:id/wallpaper_image").exists:
#                 self.device(resourceId="com.tct.launcher:id/wallpaper_image").click.wait()
            if self.device(text="Done").exists:
                self.device(text="Done").click.wait()
                self.device.delay(1)
            self.device.press('home')
            self.device.delay(2)
            if self.device(resourceId="com.google.android.googlequicksearchbox:id/hint_text_alignment").exists:
                return True
            return False
        except Exception:
            self.logger.error(traceback.format_exc())
            return False
        finally:
            self.backToHome()
            
    def enterFolder(self, _store="Internal storage", folderName="APK"):
        self.logger.info('Enter %s, Folder: %s' %(_store, folderName))
        if self.device(text='GOT IT').exists:
            self.device(text='GOT IT').click.wait()
            self.device.delay(1) 
        if self.enterStorage(_store):
            self.logger.info('scroll to files')
            self.device.swipe(500,1900,500,900,20)     # 使用滑动代替

            # listItem = self.device(resourceId="com.android.settings:id/list")
            # listItem.scroll.vert.to(text="Files")
            self.device(text="Files").click.wait()

            # 有的时候进入files直接，进到了APK目录下了
            if self.device(resourceId="android:id/title", textContains=".apk"):
                self.logger.info('already in apk folder')
                return True
            listItem_2=self.device(resourceId="com.google.android.documentsui:id/dir_list")
            if not listItem_2.scroll.vert.to(text=folderName):
                self.logger.info('No Folder: %s' % folderName)
                return False
            folderItem = self.device(text=folderName)
            folderItem.click.wait()
            self.device.delay(2)
    
    def enterStorage(self, _store="Internal storage"):
        self.logger.info("Enter the %s" % _store)
        return self.enterSubSetting("Storage")
        # if _store.lower() == "internal storage":
        #     self.device(text ="Internal shared storage").click.wait()
        # else:
        #     storeItem = self.device(resourceId="com.jrdcom.filemanager:id/sd_name")
        #     storeItem.click()
        # self.device.delay(3)
        # if self.device(text ="Storage").exists:
        #     self.logger.info("Enter the %s successful" % _store)
        #     return True
        # self.logger.warning("Enter the %s fail!" % _store)
        # return False
    def enterSettings(self):
        self.logger.debug('enter settings')
        self.start_activity(setting_app_package, setting_app_activity)
        self.device.delay(2)
        if self.device(textContains="Search settings").exists:
            self.logger.debug("enter Settings successful")
            return True
        self.logger.debug("enter Settings fail")
        return False
    
    def enterSubSetting(self, titleName):
        self.enterSettings()
        #listItem.child_by_text(titleName, text =titleName).click.wait()
        self.device.delay(2)
        if titleName=="SIM cards" or titleName=="Data usage":
            self.device(text ="Network & internet").click.wait()
            self.device(text =titleName).click.wait()
            if self.device(text="Preferred SIM for").exists:
                self.logger.info("Enter the %s successful" % titleName)
                return True
            if self.device(text="Cellular data").exists:
                self.logger.info("Enter the %s successful" % titleName)
                return True
        else:
            listItem = self.device(scrollable=True)
            if listItem.scroll.vert.to(text =titleName):
                self.device(text =titleName).click.wait()
        if self.device(description="Navigate up").exists:
            self.logger.info("Enter the %s successful" % titleName)
            return True
        self.logger.info("Enter the %s fail!" % titleName)
        return False
    
    def enterNavMenu(self):
        for _ in range(3):
            self.device.press("home")
            self.device.delay(1)
            self.device.swipe(500,1000,500,200,20)
            self.device.delay(1)
            if self.device(resourceId="com.tcl.android.launcher:id/search_box_input").exists:
                self.logger.info("Enter Navmenu successfully!")
                return True
        self.logger.info("Enter Navmenu fail!")
        return False 
        
    def backToMenu(self):
        for _ in range(3):
            if self.device(resourceId="com.android.launcher3:id/apps_list_view").exists:
                break
            self.device.press("back")
            self.device.delay(1)
        else:
            self.device.press("home")
            self.device.delay(2)
            self.device(descriptionMatches="(?i)Apps list").click()
            self.device.delay(2) 
    def changeIconOnNavMenu(self):
        if self.device(resourceId="com.tcl.android.launcher:id/all_apps_sort_order_settings").exists:
            self.device(resourceId="com.tcl.android.launcher:id/all_apps_sort_order_settings").click.wait()
        if self.device(text="By name").isChecked():
            self.device.press('back')
        else:
            self.device(text="By name").click.wait()
        self.device.delay(1)
                
    def createFolder(self):
        self.logger.info('Create Folder on home screen')
        self.enterNavMenu()
        self.changeIconOnNavMenu()
        for i in range(4):
            _index = 0
            for j in range(10):
                _index += 1
                self.logger.info('Drag %s icon to home screen......' % (i*10+j+1))
                self.enterNavMenu()
                count=self.device(resourceId='com.tcl.android.launcher:id/icon').count
                item = self.device(resourceId='com.tcl.android.launcher:id/icon', index=_index)
#                 item.long_touch(4)
#                 count_new = self.device(className='android.widget.TextView').getChildCount()
#                 self.device.delay(1)
#                 if count_new==count:
                item.drag.to(x=540, y=839,steps=10)
                #item.drag.to(x=285, y=1640, steps=40)
                #item.drag.to(x=220, y=265)
                
        if self.device(description="Folder: Unnamed Folder").exists:
            self.device(description="Folder: Unnamed Folder").click()
            self.device.delay(1)
            self.device.press("home")
            return True
        return False
#         else:
#             self.device.start_activity(setting_app_package,setting_app_activity)
#             self.device.delay(1)
#         if self.device(text="Storage").exists:
#             self.device(text="Storage").click()
#             self.device.delay(1)
#         lstView = self.device(resourceId='com.jrdcom.filemanager:id/phone_name', index=0) 
#         print lstView.getText()
#         if lstView.getText() == "Internal storage":
#             return True
#         return False
    
    def deleteFolder(self):
        self.logger.info('Delete Folder')
        for _ in range(3):
            folder_item = self.device(description="Folder: Unnamed Folder")
            if folder_item.exists:
                folder_item.drag.to(x=847, y=52, steps=40)
                self.device.delay(2)
            if not folder_item.exists:
                self.logger.info('Delete Folder successfully!')
                return True
        self.logger.info('Delete Folder fail!')
        return False
        
    def openFolder(self):
        self.logger.info('Open Folder')
        if self.device(text='GOT IT').exists:
            self.device(text='GOT IT').click.wait()
            self.device.delay(1)
        for _ in range(3):
            folder_item = self.device(description="Folder: Unnamed Folder")
            if folder_item.exists:
                folder_item.click.wait()
                self.device.delay(2)
            if self.device(text='Unnamed Folder').exists:
                self.logger.info('Open Folder successfully!')
                return True
#                 self.device.swipe(300,1400,300,200)
#                 self.device.delay(2)
#                 if self.device(text="Files").exists:
#                     self.device(text="Files").click()
#                     self.device.delay(2)
#                 else:
#                     self.createFolder()
#                 if self.device(resourceId='com.android.documentsui:id/dir_list').exists:
#                     break
        if self.device(text='Unnamed Folder').exists:
            return True
        return False
    
    def closeFolder(self):
        self.logger.info('Close Folder')
        if self.device(resourceId='com.tcl.android.launcher:id/cy_folder_page').exists:
            self.device.press('home')
            self.device.delay(2)
            return True
        return False
    
    def removeApp(self, appName):
        self.logger.info('Remove App on home screen: '+appName)
#         apps=['Secure Net Wi-Fi','Accessories','Amap ','Fill','Outlook','Keep','Mein Vodafone','Tips','Vodafone MyTone','Cardboards','Feedback']       
#         if appName in apps:
        if self.device(text=appName).exists:
            self.device(text=appName).drag.to(x=847, y=52, steps=40)
            self.device.delay(1)
#         else:
#             if self.device(description=appName).exists:
#                 self.device(description=appName).drag.to(x=240,y=51)
#                 self.device.delay(1)
#             if self.device(text=appName).exists:
#                 self.device(text=appName).drag.to(x=395,y=305,steps=40)  
#                 self.device.delay(1) 
    
    def getPageCount(self):
        if self.device(text='GOT IT').exists:
            self.device(text='GOT IT').click.wait()
            self.device.delay(1)
        return 2
#         if self.device(resourceId='com.android.launcher:id/page_indicator').exists:
#             return self.device(resourceId='com.android.launcher:id/page_indicator').getChildCount()
    
    def clearAllShortcut(self, pageCount=10):
        for loop in range(pageCount):
            self.backToHome()
            self.device(className='android.view.ViewGroup', index=0).swipe.left()
            self.device.delay(2)
            if self.device(resourceId="com.google.android.googlequicksearchbox:id/hint_text_alignment").exists:
                self.logger.info("No shortcut on other page!")
                return True
            self.logger.info('Clear all shortcut for page: %s' % (loop+1))
            count = self.icon_container.childCount  # 有2个ViewGroup
            self.logger.info("found items in current page: {}".format(count))
            for i in range(count):
                # lstView = self.device(className='android.view.ViewGroup', index=1)
                self.logger.info("remove item - {}".format(i+1))
                self.icon_container.child(index=0).drag.to(x=847, y=52, steps=40)
                self.device.delay(timeout=1)
                # des = lstView.child(index=0).get_text()
                # if des == '':
                #     self.logger.info("it is a folder or something, just drag it")
                #     lstView.child(index=0).drag.to(x=847, y=52, steps=40)
                #     continue
                # self.device.delay(1)
                # self.removeApp(des)
        self.device(className='android.view.View', index=0).swipe.left()
        self.device.delay(2)
        if not self.device(resourceId="com.google.android.googlequicksearchbox:id/search_edit_frame").exists:
            self.logger.info("Fail to clear all other page!")
            return False
#         if self.device(className='android.view.ViewGroup', index=0).childCount != 0:
#             self.logger.info('Cannot clear page!')
#             return False
                
    def addShortcut(self, pageCount=5):
        self.enterNavMenu()
        self.changeIconOnNavMenu()
        self.backToHome()
        for loop in range(pageCount):
            self.logger.info('Add Shortcut for Page: %s' % (loop+1))
            for app in range(30):
                self.device.swipe(500,1000,500,200,20)
                self.device.delay(1)
                item = self.device(resourceId='com.tcl.android.launcher:id/icon', index=app+1)
                if app == 0:
                    item.drag.to(x=1100, y=200,steps=20)
                    self.device.delay(1)
                else:
                    item.drag.to(x=124+(app//6)*208, y=259+(app%6)*290, steps=30)
                    '''
                    x=a+(app//b)*c,y=d+(app%b)*e
                    a:first column abscissa
                    b:first column icon number
                    c:one line adjacent icon abscissa difference
                    d:first column ordinate
                    e:one row adjacent icon ordinate difference
                    '''
                    self.device.delay(1)
            self.device.delay(4)
            if self.icon_container.childCount < 25:
                self.logger.info('Add Shortcut for Page: %s fail'  % (loop+1))
                return False
        self.logger.info('Add Shortcut successfully!')
        return True
    
    def prepareIdle(self):
        self.logger.info('Prepare Idle Screen')
        self.backToHome()
        for _ in range(4):
            self.device.swipe(500,1000,500,200,20)
            self.device.delay(1)
            item = self.device(resourceId='com.tcl.android.launcher:id/icon', index=1)
            item.drag.to(x=1100, y=200,steps=20)
            self.device.delay(1)
        self.device.press('home')
        
    def changeIdle(self):
        self.logger.info('Change Idle Screen')
        self.backToHome()
        self.device.press("menu")
        self.device.delay(2)
        for _ in range(4):
            self.device(resourceId='com.tcl.android.launcher:id/workspace').swipe.left()
        self.device.delay(1)
        self.device(resourceId='com.tcl.android.launcher:id/workspace').drag.to(-500,1000,steps=50)   
        self.device.delay(1)
        self.device.press('home')
        return True
                
    def addDynamicApp(self, appName):
        self.logger.info('Add Dynamic App to home screen: '+appName)
        self.enterNavMenu()
        item = self.device(text=appName)
        item.drag.to(x=540, y=1000,steps=10)
        if self.device(text=appName).exists:
            return True
        return False
            
    def addWidget(self, pageCount = 5):
        flag = True
        for loop in range(pageCount):
            self.logger.info('Add Widget for Page: %s' % (loop+1))
            self.device.press('menu')
            self.device.delay(2)
            self.device(text="Widgets").click.wait()
            self.device.delay(1)
            listView = self.device(resourceId='com.tcl.android.launcher:id/widgets_list_view')
            if listView.exists:
#                     if loop > 0 and loop1 == 0:
#                         self.device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=480,y=399.5,steps=40)
#                         self.device.delay(2)
#                     elif loop == 0 and loop1 == 0:
#                         self.device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=320,y=634.5,steps=40)
#                         self.device.delay(2)
#                     else:
                self.device(resourceId='com.tcl.android.launcher:id/widget_dims', text = "4 × 4").drag.to(x=500,y=1000,steps=40)
                self.device.delay(2)
#                     self.device(resourceId='com.android.launcher3:id/widget_preview', instance = 2).drag.to(x=380,y=399.5,steps=40)
#                     self.device.delay(2)
        lstView = self.device(resourceId='com.google.android.calendar:id/widgetmonth_header') 
        if lstView.exists:
            self.logger.debug("Add widget successfully!")
            return True
        self.logger.debug("Add widget fail!")
        return False
#                 if listView.exists:
#                     if loop > 0 and loop1 == 0: 
#                         self.device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=1420,y=800,steps=40)
#                         self.device.delay(2)
#                         self.device(resourceId='com.android.launcher3:id/workspace').swipe.left()
#                         self.device.delay(1)
#                     elif loop == 0 and loop1 == 0:
#                         self.device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=480,y=980,steps=40)
#                         self.device.delay(2)
#                     else:
#                         self.device(resourceId='com.android.launcher3:id/widget_preview', instance = loop1).drag.to(x=750,y=1080,steps=40)
#                         self.device.delay(2)                        
#             lstView = self.device(className='android.view.ViewGroup', instance=1) 
#             flag &= (lstView.childCount == 2)
#         if flag:
#             return True
#         return False
            
    def readFile(self, name='apk.txt'):  
        fi = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configure", name))
        try:
            return fi.readlines()                 
        finally:
            fi.close()
                           
            
    def uninstallAPK(self):
        lines = self.readFile('package.txt')
        for line in lines:
            self.logger.info('Uninstall APK: %s' % line)
            subp = subprocess.Popen('adb uninstall %s' % line, shell=True)
            subp.communicate()
        
            
    def installAPK(self, number = 40):
        lines = self.readFile()
        # flag = True
        failed_apps = []

        for loop in range(number):
            self.device.delay()
            listView = self.device(resourceId='com.tcl.tct.filemanager:id/list_view')
            app_name = lines[loop].strip()
            if listView.exists:
                self.logger.info('Install APK: %s' % lines[loop].strip())
                if not listView.scroll.vert.to(resourceId='com.tcl.tct.filemanager:id/edit_adapter_name', text=app_name):
                    self.logger.warning('APK named %s not exists!' % lines[loop].strip())
                    continue
                if not self._install(app_name):
                    failed_apps.append(app_name)

        if len(failed_apps) == 0:
            return True
        else:
            self.logger.error("******* installed failed apps: {} ******".format(failed_apps))
            return False

    def _install(self, name):
        self.device(text=name).click()
        self.device.delay(2)
        if self.device(resourceId='android:id/button1',text='CONTINUE').exists:
            self.device(resourceId='android:id/button1',text='CONTINUE').click.wait()
            self.device.delay(1)
        if self.device(resourceId='com.android.packageinstaller:id/ok_button',text='NEXT').exists:
            self.device(resourceId='com.android.packageinstaller:id/ok_button',text='NEXT').click.wait()
            self.device.delay(1)
        if self.device(resourceId='com.android.packageinstaller:id/ok_button',text='Next').exists:
            self.device(resourceId='com.android.packageinstaller:id/ok_button',text='Next').click.wait()
            self.device.delay(1)
        if self.device(resourceId='com.android.packageinstaller:id/ok_button',text='INSTALL').exists:
            self.device(resourceId='com.android.packageinstaller:id/ok_button',text='INSTALL').click.wait()
            self.device.delay(1)
        if self.device(text='INSTALL').exists:
            self.device(text='INSTALL').click.wait()
        self.device.delay(1)
        self.device(text='Installing…').wait.gone(timeout=120000)
        self.device.delay(1)
        item = self.device(text='App installed.')
        if item.exists:
            self.device(text='DONE').click.wait()
            self.device.delay(2)
            self.logger.info("app {} installed".format(name))
            return True
        else:
            if self.device(text='DONE').wait.exists(timeout=1000):
                self.device(text='DONE').click.wait()
                self.device.delay(2)

        self.logger.error("******* install app {} failed ******".format(name))
        return False
        # for loop in range(number):
        #     self.device.delay()
        #     if not self.device(text="APK").exists:
        #         self.enterFolder(_store='Storage')
        #
        #     self.sel_list_view()
        #     listView = self.device(resourceId='com.google.android.documentsui:id/dir_list')
        #     if listView.exists:
        #         self.logger.info('Install APK: %s' % lines[loop].strip())
        #         if not listView.scroll.vert.to(resourceId='android:id/title', text=lines[loop].strip()):
        #             self.logger.warning('APK named %s not exists!' % lines[loop].strip())
        #             continue
        #         self.device(text=lines[loop].strip()).click.wait()
        #         self.device.delay(2)
        #         if self.device(resourceId='android:id/button1',text='CONTINUE').exists:
        #             self.device(resourceId='android:id/button1',text='CONTINUE').click.wait()
        #             self.device.delay(1)
        #         if self.device(resourceId='com.android.packageinstaller:id/ok_button',text='NEXT').exists:
        #             self.device(resourceId='com.android.packageinstaller:id/ok_button',text='NEXT').click.wait()
        #             self.device.delay(1)
        #         if self.device(resourceId='com.android.packageinstaller:id/ok_button',text='Next').exists:
        #             self.device(resourceId='com.android.packageinstaller:id/ok_button',text='Next').click.wait()
        #             self.device.delay(1)
        #         if self.device(resourceId='com.android.packageinstaller:id/ok_button',text='INSTALL').exists:
        #             self.device(resourceId='com.android.packageinstaller:id/ok_button',text='INSTALL').click.wait()
        #             self.device.delay(1)
        #         if self.device(text='INSTALL').exists:
        #             self.device(text='INSTALL').click.wait()
        #         self.device.delay(1)
        #         self.device(text='Installing…').wait.gone(timeout=120000)
        #         self.device.delay(1)
        #         item = self.device(text='App installed.')
        #         flag &= item.exists
        #         if item.exists:
        #             self.device(text='DONE').click.wait()
        #             self.device.delay(2)
        #     else:
        #         self.logger.warning('No APK in folder !')
        #         return False
        # if flag:
        #     return True
        # return False

    def sel_list_view(self):
        if self.device(resourceId="com.google.android.documentsui:id/sub_menu_list").wait.exists(timeout=1000):
            self.device(resourceId="com.google.android.documentsui:id/sub_menu_list").click()
            self.device.delay(timeout=1)
                
if __name__ == "__main__":
    # d = common.Device()
    #print d.get_current_packagename()
    l = Launcher(d)
    l.changeIdle()
#     l.clearAllShortcut()
#     l.createFolder()
#     item = l.device(className='android.view.ViewGroup',index=1).childCount
#     print(item)