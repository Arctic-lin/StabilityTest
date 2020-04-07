# -*- coding: UTF-8 -*-
import re, random, sys, traceback
from lib import common
from lib.common import Common
from _socket import timeout
from pip._vendor.distlib.resources import Resource
contact_package = 'com.google.android.contacts'
contact_activity = 'com.android.contacts.activities.PeopleActivity'
# contact_package = 'com.tct.contacts'
# contact_activity = 'com.android.contacts.activities.PeopleActivity'

class Contacts(Common):

    """Provide common functions for scripts, such as launching activity."""
    
    def __init__(self, device, log_name="CONTACT"):
        Common.__init__(self, device,log_name)

    def enter_contact(self):     
        self._logger.debug('enter contact')
        self._device.start_activity(contact_package,contact_activity)
        self._device.delay(2)
        for _ in range(2):
            if self._device(textMatches="(?i)allow").exists:
                self._device(textMatches="(?i)allow").click.wait()
                self._device.delay(2)
            else:
                break
        if self._device.currentPackageName == contact_package:
            self._logger.debug('enter contact success!')
            return True
        else:
            self.backToHome()
            self._logger.debug('enter contact fail!')
            return False
    
    def clearAllAutoTestContacts(self):
        try:
            self.enter_contact()
            if not self._device(textStartsWith="AutoTest").exists:
                return True
            if self._device(scrollable=True).exists:
                self._device(scrollable=True).fling.toBeginning(max_swipes=3)
            self._device.delay(2)
            for _ in range(50):
                if not self._device(textStartsWith="AutoTest").exists:
                    return True
                self.delete_contact_item()
        except Exception:
            self.save_fail_img()
            common.log_traceback(traceback.format_exc())
        
    def back_to_contact(self):
        self._logger.debug('Back to contact')
        for _ in range(5):
            if self._device(description='Create contact').exists:
                break
            self._device.press("back")
            self._device.delay(1)
        else:
            self.enterApp("Contacts")  
        
    def delete_contact_item(self, name=""):
        self._logger.debug('delete the contact')
        if self._device(text='Contact list is empty').exists:
            self._logger.warning('No Contacts on Phone')
            return True
        listItem = self._device(className="android.widget.ListView")
        if not name:            
            listItem.child(resourceId="com.tct.contacts:id/cliv_name_textview", instance=0).click.wait()
            self._device.delay(2)
        else:
            if listItem.scroll.to(text=name):
                self._device(resourceId="com.tct.contacts:id/cliv_name_textview", text = name).click.wait()
                self._device.delay(2)
            else:
                self._logger.warning("no contact named %s exists on phone!" % name)
                return False
        if self._device(description="More options").exists:
            self._device(description="More options").click()
            self._device.delay(2)
        if self._device(text="Delete").exists:
            self._device(text="Delete").click.wait()
            self._device.delay(1)
        if self._device(resourceId="android:id/button1").exists:
            self._device(resourceId="android:id/button1").click.wait()
            self._device.delay(2)
        if not self._device(text=name).exists:
            self._logger.info("Delete contact %s successful" % name)
            return True
        self._logger.info("Delete contact %s fail!" % name)
        return False
    
    def deleteContactOnSim(self, name=""):
        self.enterSIMManagerUi()
        if not name:
            lstItem = self._device(className="android.widget.ListView")
            delItem = lstItem.child(className="android.widget.TwoLineListItem", index=0)
        else:
            delItem = self._device(text=name)
        delItem.long_touch()
        self._device.delay(1)
        self._device(text="Delete").click()
        self._device.delay(2)
        if not self._device(text=name).exists:
            return True
        return False
    
    def enterSIMManagerUi(self):
        title = self._device(className="android.widget.TextView",textStartsWith="Manage SIM")
        if title.exists:
            return True
        for option in ["More options", "Manage SIM contacts", "More options", "Add SIM contact"]:
            if self._device(text=option).exists:
                self._device(text=option).click()
            elif self._device(description=option).exists:
                self._device(description=option).click()
            self._device.delay(2)
        if title.exists:
            return True
        return False
    
    def clearAllSimContacts(self):
        self.enterSIMManagerUi()
        if self._device(resourceId="android:id/empty").exists:
            return True
        self._device(description="More options").click()
        self._device.delay(1)
        self._device(text="Delete all SIM contacts").click()
        if self._device(text="Successfully deleted all contacts from SIM").wait.exists(timeout=120000):
            self._device(text="OK").click()
            self._device.delay(2)
            return True
        return False

    def clear_all_contacts(self):
        self._logger.info("Clear all contacts")
        lstItem = self._device(className="android.widget.ListView")
        if lstItem.getChildCount == 2:
            return True
        self._device(description='More options').click()
        self._device.delay(2)
        self._device(text='Delete').click()
        self._device.delay(2)
        self._device(resourceId="com.android.contacts:id/select_all_check").click()
        self._device.delay(2)
        self._device(description='Done').click()
        self._device.delay(2)
        self._device(text='OK').click()
        self._vc.sleep(3)
        for _ in range(15):
            self._device.delay(2)
            if lstItem.getChildCount() == 2:
                self._logger.debug("Clear all contacts successful!")
                return True
            self._vc.sleep(2)
        self._logger.debug('contact delete fail!')            
        return False
    
    def get_contact_num(self):
        lstItem = self._device(className="android.widget.ListView")
        if lstItem.getChildCount == 2:
            return 0
        self._device(description='More options').click()
        self._device.delay(2)
        self._device(text='Delete').click()
        self._device.delay(2)
        self._device(resourceId="com.android.contacts:id/select_all_check").click()
        self._device.delay(2)
        countText = self._device(resourceId="com.android.contacts:id/selected_contact_count").getText()
        self._device.press("back")
        self._device.delay(1)
        return int(countText)   
        
    def create_contact(self, name="", phoneNo=10010, account="Phone"):
        self._logger.debug("Create contact")
        import string
        if self._device(description="Create new contact").exists:
            self._device(description="Create new contact").click.wait()
        if self._device(description="Create contact").exists:
            self._device(description="Create contact").click.wait()
        self._device.delay(2)
        if self._device(textContains = "Store the contact to").exists:
            self._device(textContains = "Phone",resourceId = "android:id/text1").click()
            self._device.delay(2)  
        if not name:
            name = "AutoTest_"+"".join(random.sample(string.ascii_letters, 4))
        if self._device(text="First name").exists:
            self._device(text="First name").set_text(name)
        if self._device(text="Name").exists:
            self._device(text="Name").set_text(name)
        if self._device.isKeyboardShown():
            self._device.press("back")
            self._device.delay(1)
        if self._device(text="Phone", className="android.widget.EditText").exists:
            self._device(text="Phone", className="android.widget.EditText").set_text(str(phoneNo))
        if self._device(text="Primary number", className="android.widget.EditText").exists:
            self._device(text="Primary number", className="android.widget.EditText").set_text(str(phoneNo))
        self._device(resourceId="com.google.android.contacts:id/menu_save").click.wait()
        self._logger.debug("Save contact")
        self._device.delay(2)
        number = "".join(re.findall('\d',self._device(resourceId="com.google.android.contacts:id/header").getText()))
        #number = "".join(self._device(resourceId="com.tct.contacts:id/header").getText().split())
        if self._device(resourceId="com.google.android.contacts:id/large_title").get_text() == name and number == str(phoneNo):
            self._logger.debug("Create contact successful")
            self._device.press("back")
            self._device.delay(2)
            return True
        self._logger.debug("Create contact fail!")
        return False 
    
    def enter_create_contact(self):
        if self._device(description="Create contact").exists:
            self._device(description="Create contact").click.wait()
            self._device.delay(2)
        if self._device(textMatches="(?i)Keep local.*").exists:
            self._device(textMatches="(?i)Keep local.*").click()
        if self._device(resourceId="com.android.contacts:id/right_button").exists:
            self._device(resourceId="com.android.contacts:id/right_button").click.wait()
            self._device.delay(2)
        if self._device(resourceId="com.google.android.contacts:id/menu_save").exists:
            return True
                
            
    #type = takePhoto & choose photo
    def changePhoto(self,type="takePhoto"):  
        self._logger.debug("change Phote:"+type)
        for _ in range(5):
            if self._device(resourceId ="com.google.android.contacts:id/photo_icon").exists:
                self._device(resourceId ="com.google.android.contacts:id/photo_icon").click.wait()
                self._device.delay(1)
                if self._device (text="Remove photo").exists:
                    self._device (text="Remove photo").click()
            if  self._device(text ="Cancel").exists:
                break
        # if self._device(resourceId = "com.tct.dialer:id/camera_gallery_view").wait.exists(timeout=10000):
        #     self._device(resourceId = "com.tct.dialer:id/camera_gallery_view").click.wait()
        #     self._device.delay(1)
        if type == "takePhoto":
            if self._device(textMatches = "(?i)take.*photo").exists:
                self._device(textMatches = "(?i)take.*photo").click.wait()
            self._device.delay(2)
            if self._device(resourceId = "com.tcl.camera:id/shutter_button").wait.exists(timeout=10000):
                self._device(resourceId = "com.tcl.camera:id/shutter_button").click.wait()
                self._device.delay(4)
            if self._device(resourceId = "com.tcl.camera:id/btn_done").wait.exists(timeout=10000):
                self._device(resourceId = "com.tcl.camera:id/btn_done").click()
            if self._device(text="Gallery").exists:
                self._device(text="Gallery").click()
                self._device.delay(2)
                if self._device(text="ALWAYS").exists:
                    self._device(text="ALWAYS").cick()
            self._device.delay (2)
            if self._device(resourceId="com.tclhz.gallery:id/saveWallpaperOrCrop").exists:
                self._device (resourceId="com.tclhz.gallery:id/saveWallpaperOrCrop").click()
        else:
            self._device(textMatches = "(?i)choose.*photo").click.wait()    
            self._device.delay(2)
            # if self._device(text = "Pictures").exists:
            #     self._device(text = "Pictures").click.wait()
            #     self._device.delay(3)
            if self._device(text = "Gallery").exists:
                self._device(text = "Gallery").click()
                self._device.delay(3)     
                if self._device(text = "ALWAYS").exists:
                    self._device(text = "ALWAYS").click()
            self._device.delay(3)
            if self._device(text="All").exists:
                self._device (text="All").up (resourceId="com.tclhz.gallery:id/album_item_cover").click()
                self._device.delay(2)
                if self._device(resourceId="com.tclhz.gallery:id/comments_image_item").exists:
                    self._device (resourceId="com.tclhz.gallery:id/comments_image_item").click()
                self._device.delay (2)
                if self._device (resourceId="com.tclhz.gallery:id/saveWallpaperOrCrop").exists:
                    self._device (resourceId="com.tclhz.gallery:id/saveWallpaperOrCrop").click ()
            # if self._device(description = "Show roots").exists:
            #     self._device(description = "Show roots").click()
            #     self._device.delay(3)
            # if self._device(resourceId="com.google.android.apps.photosgo:id/single_photo",instance = 0).exists:
            #     self._device(resourceId="com.google.android.apps.photosgo:id/single_photo",instance = 0).click()
            #     self._device.delay(2)
            # if self._device(resourceId = "com.tclhz.gallery:id/comments_image_item",instance = 0).exists:
            #     self._device(resourceId = "com.tclhz.gallery:id/comments_image_item",instance = 0).click()
            #     self._device.delay(2)
            # if self._device(resourceId = "com.google.android.apps.photos",instance = 1).exists:
            #     self._device(resourceId = "com.google.android.apps.photos",instance = 1).click.wait()
            #     self._device.delay(2)
            # if self._device(descriptionStartsWith = "Photo taken on",instance = 0).exists:
            #     self._device(descriptionStartsWith = "Photo taken on",instance = 0).click.wait()
            #     self._device.delay(2)
        # if self._device(text = "Photos").exists:
        #     self._device(text = "Photos").click()
        #     self._device.delay(2)
        # if self._device(text = "JUST ONCE").exists:
        #     self._device(text = "JUST ONCE").click()
        #     self._device.delay(2)
        # if self._device(resourceId = "com.tcl.camera:id/btn_done").exists:
        #     self._device(resourceId = "com.tcl.camera:id/btn_done").click.wait()
        #     self._device.delay(3)
        # if self._device(text = "Save copy").wait.exists(timeout=5000):
        #     self._device(text = "Save copy").click()
        #     self._device.delay(2)
        if self._device(resourceId = "com.google.android.contacts:id/photo_icon").wait.exists(timeout=10000):
            self._device(resourceId = "com.google.android.contacts:id/photo_icon").click()
            self._device.delay(2)
            if self._device(text="Remove photo").exists:
                self._device.press("back")
                return True
            else:
                return False
    
    def discard_contact(self):        
        #delete the new contact
        self._device.press.back()
#         if self._device(text = "CANCEL").exists:
#             self._device(text = "CANCEL").click()     
        self._device.delay(1)
        if self._device(text="Discard").exists:
            self._device(text="Discard").click.wait()
            self._device.delay(1)
        if self._device(resourceId="android:id/button2").exists:
            self._device(resourceId="android:id/button2").click()
        return True
    
    def swipeContacts(self):
        for _ in range(10):
            self._device(resourceId ="com.google.android.contacts:id/cliv_name_textview",instance=5).swipe.up(steps = 5)
        for _ in range(10):
            self._device(resourceId ="com.google.android.contacts:id/cliv_name_textview",instance=5).swipe.down(steps = 5)
        
        return True
    
    def findContact(self):
        self._device(resourceId ="com.google.android.contacts:id/open_search_bar_text_view").click.wait()
        self._device.delay(2)
        if self._device(text ="Search contacts").exists and self._device(description="Open navigation drawer").exists:
            self._device(text ="Search contacts").set_text("CD")
            self._device.delay(2)
        if self._device.isKeyboardShown():
            self._device.press.back()
            self._device.delay(2)
        if self._device(resourceId ="com.google.android.contacts:id/search_result_list").getChildCount() > 0:
            return True
        return False
    
    def testCallContact(self):
        if self._device(resourceId ="com.google.android.contacts:id/cliv_name_textview",instance = 2).wait.exists(timeout= 2000):
            self._device(resourceId ="com.google.android.contacts:id/cliv_name_textview",instance = 2).click()
            self._device.delay(2)
            self._device(descriptionContains = "Call").click()
            self._device.delay(5)
            maxloop = 0
        for _ in range(10):
            if self._device(resourceId="com.google.android.dialer:id/contactgrid_bottom_timer").exists:
                self._device.delay(5)
                if self._device(description="End call").exists:
                    self._device (description="End call").click()
                return True
            callState = self._device.get_call_state()
            if callState=="incall":
                if self._device(description="End call").exists:
                    self._device (description="End call").click()
                return True
            self._device.delay(2)
        return False
#             while not self._device(resourceId ="com.google.android.dialer:id/contactgrid_bottom_timer").exists:
#                 self._logger.debug("The call is calling")
#                 self._device.delay(3)
#                 if maxloop > 10:
#                     return False
#                 maxloop +=1
#             else:
#                 self._logger.debug("The call is success")
#                 self._device.delay(5)
#                 self._logger.info("End the call")
#                 endBtn = self._device(resourceId="com.tct.dialer:id/incall_end_call")
#                 if endBtn.exists:
#                     endBtn.click()
#                 elif self._device.get_call_state() == "incall" or self._device.get_call_state() == "ringing":
#                     self._device.shell_adb("shell input keyevent KEYCODE_ENDCALL")
#                 return True
#             return False
            
    def testReEnterDetailsContact(self):
        if self._device(resourceId ="com.google.android.contacts:id/cliv_name_textview",instance = 2).wait.exists(timeout= 2000):
            self._device(resourceId ="com.google.android.contacts:id/cliv_name_textview",instance = 2).click.wait()
            self._device.delay(3)
            if self._device(description ="Set up Duo video calling").exists:
                return True        
        return False    
    
    def testEnterContactByRecent(self):
        if self.enter_contact():
            self.backToHome() 
            self._device.press("recent")
            if self._device(text="Contacts").exists:
                self._device(text="Contacts").click.wait()  
                self._device.delay(3)
                if self._device.currentPackageName == contact_package:
                    return True
        return False
        
if __name__ == "__main__":
    d = common.Device("S8EIRCOBEEFEGMCI")
    c = Contacts(d)
    c.enter_contact()
    #print d.get_current_packagename()
        