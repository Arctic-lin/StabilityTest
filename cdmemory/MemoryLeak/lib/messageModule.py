# -*- coding: UTF-8 -*-
"""Message library for scripts.
"""

import traceback
import re
from lib import common
from lib.common import Common

message_package = 'com.google.android.apps.messaging'
message_activity = '.ui.ConversationListActivity'
# message_package = 'com.google.android.apps.messaging'
# message_activity = 'com.google.android.apps.messaging.ui.conversationlist.ConversationListActivity'
StorePath_MessagePic = '/storage/self/primary/DCIM/Message+'

gallery_package = "com.tclhz.gallery"
gallery_activity = "com.tcl.gallery.app.GalleryActivity"

photos_package = "com.google.android.apps.photos"
photos_activity = ".home.HomeActivity"

recorder_package="com.tct.soundrecorder"
recorder_activity=".SoundRecorder"

contact_package = 'com.google.android.contacts'
contact_activity = 'com.android.contacts.activities.PeopleActivity'

downloads_package = "com.android.documentsui"
downloads_activity = ".files.FilesActivity"

class Message(Common):

    """Provide common functions for scripts, such as launching activity."""
    
    def __init__(self, device, log_name="MESSAGE"):
        Common.__init__(self, device, log_name)
    
    def enter_message(self):
        self._logger.debug("Launch Message.")
        self.backToHomeFromMessage()
        self._device.start_activity(message_package,message_activity)
        self._device.delay(2)
        if self._device.currentPackageName == message_package:
            self.back_to_message()
            return True
        return False
    
    def back_to_message(self):
        for _ in range(5):
            if not self._device(resourceId='com.google.android.apps.messaging:id/start_new_conversation_button').exists:
                self._device.press("back")
                self._device.delay(2)
            else:
                break
        else:
            self._device.start_activity(message_package,message_activity)
            self._device.delay(2)
    
    def set_draft(self,number="1111", content="Send SMS"):
        self._device(resourceId = "com.google.android.apps.messaging:id/start_new_conversation_button").click()
        self._device.delay(2)
        self._device(resourceId="com.google.android.apps.messaging:id/recipient_text_view").set_text(number)
        self._device.delay(2)
        self._device.press("enter")
        self._device.delay(2)
        if self._device (resourceId="com.google.android.apps.messaging:id/close_button").exists:
            self._device (resourceId="com.google.android.apps.messaging:id/close_button").click.wait ()
        conItem = self._device(resourceId="com.google.android.apps.messaging:id/compose_message_text")
        for _ in range(2):
            if conItem.exists:
                self._logger.debug('input sms content: '+content)
                conItem.set_text(content)
                self._logger.debug('input sms content success')
                break
        self._device.delay(3)
            
    def sendSMS(self, number="10012", content="Send SMS"):
        try:
            self.set_draft()
            self._device(resourceId='com.google.android.apps.messaging:id/send_message_button_icon').click()
            self._device.delay(3)
            self._logger.debug('sending...')
            message_status = self._device(resourceId="com.google.android.apps.messaging:id/message_status",textMatches="Now.*SMS")
            for _ in range(5):
                if message_status.exists:
                    self._logger.debug("The message sent successfully!")
                    if self.backToHomeFromMessage():
                        return True
                self._device.delay(3)
        except Exception:
            self.save_fail_img()
            common.log_traceback(traceback.format_exc())
            return False

    def newAndSendMessage(self, number="1111", content="Send SMS"):
        self._logger.debug("Start to new Message.")
        if not self.enter_message():
            self.enter_message()
        self._device.delay (2)
        if self.sendSMS(number,content):
            self.backToHome()
            return True
        return False 
                
    def frontBackSwitch(self, picker="back camera"):
        toggleBtn = self._device(resourceId="com.google.android.apps.messaging:id/camera_swapCamera_button")
        if not toggleBtn.getContentDescription().lower().startswith(picker.lower()):
            toggleBtn.click()
            self._device.delay(2)    
                      
           
    def add_and_delete_attachment(self,_type):
        if self._device (resourceId="com.google.android.apps.messaging:id/close_button").exists:
            self._device (resourceId="com.google.android.apps.messaging:id/close_button").click.wait ()
        for _ in range(5):
            if  self._device(resourceId='com.google.android.apps.messaging:id/c2o_category_toggle_icon').exists:
                break
            self._device(resourceId='com.google.android.apps.messaging:id/plus_button').click.wait()
            self._device.delay(1)
        self._logger.debug("Take %s" %_type)
        if _type == "Photo":
            preview = self._device(resourceId="com.google.android.apps.messaging:id/image_attachment_rounded_view")
            self._device(resourceId="com.google.android.apps.messaging:id/camera_gallery_button").click.wait()
            self._device.delay(1)
            if self._device (resourceId="com.google.android.apps.messaging:id/fullscreen_camera_button").exists:
                self._device (resourceId="com.google.android.apps.messaging:id/fullscreen_camera_button").click ()
                self._device.delay(2)
            elif self._device(resourceId="com.google.android.apps.messaging:id/buttons_portrait").exists:
                self._device (resourceId="com.google.android.apps.messaging:id/buttons_portrait").click()
            self._device.delay(2)
            if self._device(description="Photo mode").exists:
                self._device (description="Photo mode").click.wait()
            self._device.delay (1)
            if self._device (description="Take photo").exists:
                self._device (description="Take photo").click.wait ()
                self._device.delay (2)
            if self._device (resourceId="com.google.android.apps.messaging:id/attach_button").exists:
                self._device (resourceId="com.google.android.apps.messaging:id/attach_button").click.wait ()
                self._device.delay (4)
        elif _type == "Video":
            preview = self._device (resourceId="com.google.android.apps.messaging:id/video_thumbnail_image")
            self._device (resourceId="com.google.android.apps.messaging:id/camera_gallery_button").click.wait ()
            self._device.delay (1)
            if self._device (resourceId="com.google.android.apps.messaging:id/fullscreen_camera_button").exists:
                self._device (resourceId="com.google.android.apps.messaging:id/fullscreen_camera_button").click ()
                self._device.delay(2)
            elif self._device (resourceId="com.google.android.apps.messaging:id/buttons_portrait").exists:
                self._device (resourceId="com.google.android.apps.messaging:id/buttons_portrait").click ()
            self._device.delay (1)
            if self._device (description="Video mode").exists:
                self._device (description="Video mode").click.wait()
            self._device.delay (1)
            if self._device (description="Start recording video").exists:
                self._device (description="Start recording video").click.wait ()
                self._device.delay (2)
            if self._device (description="Stop recording and attach video").exists:
                self._device (description="Stop recording and attach video").click.wait ()
                self._device.delay (2)
            if self._device (resourceId="com.google.android.apps.messaging:id/attach_button").exists:
                self._device (resourceId="com.google.android.apps.messaging:id/attach_button").click.wait ()
                self._device.delay (4)
            self._device.delay(2)
        elif _type == "Audio":
            preview = self._device(description="Play audio attachment")
            while not self._device(text="Touch and hold").exists:
                self._device.swipe (185,1358,185,1112)
                self._device.delay(2)
            self._device.delay(1)
            if self._device(text="Touch and hold").exists:
                self._device (text="Touch and hold").long_touch(5)
        if self._device(resourceId="com.google.android.apps.messaging:id/close_button").exists:
            self._logger.debug("Attach %s successfully!" %_type)
            self._logger.debug("Cancel the attachment")
            self._device(resourceId="com.google.android.apps.messaging:id/close_button").click.wait()
            self._device.delay(1)
        if not self._device(resourceId="com.google.android.apps.messaging:id/close_button").exists:
            self._logger.warning("Take %s successfully!" %_type)
            return True
        else:
            self._logger.warning("Take %s failed!" %_type)
            return False


    def enterGalleryfromMessage(self):
        if not self.enter_message():
            self.enter_message()
        self.set_draft()
        self._device(resourceId="com.google.android.apps.messaging:id/plus_button").click.wait()
        self._device.delay(2)
        while not self._device(text="Attach file").exists:
            self._device.swipe (185, 1358, 185, 1112)
            self._device.delay (2)
        if self._device(text="Attach file").exists:
            self._device (text="Attach file").click()
            self._device.delay (2)
        # if self._device (description="Show roots").exists:
        #     self._device (description="Show roots").click()
        #     self._device.delay(2)
        if self._device(text="Gallery").exists:
            self._device(text="Gallery").click()
            self._device.delay(5)
        if self._device.currentPackageName == gallery_package:
            self._logger.debug ("Enter gallary from message pass!")
            return True
        else:
            self._logger.debug("Enter gallary from message fail!")
            return False
        
    
    def takeFromMessage(self,_type):
        if not self.enter_message():
            self.enter_message()  
        self._logger.debug('Take %s from message.' % _type)
        self.set_draft()
        if self.add_and_delete_attachment(_type):
            self._logger.warning("Enter camera from message to take %s success!" % _type)
            self.backToHome()
            return True
        else:
            self._logger.warning("Enter camera from message to take %s failed!" % _type)
            self.backToHome()
            self._logger.debug ('enterAttachment failed.')
            return False

    
    def backToHomeFromMessage(self):
        for _ in range(10):
            self._device.press("back")
            self._device.delay(1)
            if self._device(resourceId="com.tcl.android.launcher:id/layout").exists:
                self._logger.debug("Back to Home from message successful!")
                return True
        return False 
                            
    def slideAndPreviewMedia(self,mediaType):
        self._logger.info("Slide and preview media:%s" % mediaType)
        self.enterGalleryfromMessage()
        if self._device(text="enterPhoto").exists:
            self._device (text="enterPhoto").up(resourceId="com.tclhz.gallery:id/album_item_cover").click()
        scroll_view = self._device(resourceId='com.tclhz.gallery:id/comments_image_item',instance=10)
        view_group=self._device(className="android.view.ViewGroup",clickable=True)
        video_widget=self._device(textMatches="\d\d:\d\d",resourceId="com.tclhz.gallery:id/moments_image_item_duration")
        if scroll_view.exists:
            for i in range(view_group.count):
                scroll_view.scroll.vert.forward(steps=10)
                self._device.delay(2)
                if mediaType == "video":
                    if video_widget.exists:
                        video_widget.click()
                        break
                elif mediaType == "image":
                    print (mediaType, view_group[i].get_child_count == 2)
                    if view_group[i].get_child_count() == 2:
                        view_group[i].click ()
                        break
        if self._device(descriptionContains="Navigate up").exists:
            self._device(descriptionContains="Navigate up").click.wait()
            self._device.delay(2)
        if self._device(resourceId="com.google.android.apps.messaging:id/close_button").exists:
            self._device(resourceId="com.google.android.apps.messaging:id/close_button").click.wait()
            self._logger.debug("Add and delete attachment successfully!")
            self._device.delay(1)
        return True
        
              
        
    
    def addSoundRecord(self,number="10010", content="test MMS", recordTimes=5):
        if not self.enter_message():
            self.enter_message() 
        if not self.enterAttachment(number,content):
            return False
#         for _ in range(2):
#             if self._device(resourceId="com.android.mms:id/record_audio").exists:
#                 self._device(resourceId="com.android.mms:id/record_audio").click()
#                 self._device.delay(1)
#                 break
#             else:
#                 self._device.swipe(300,1400,300,1000,8)
#         self._device(resourceId="com.android.mms:id/druation_bar").long_touch(recordTimes)
# #         self._device(resourceId="com.vodafone.messaging:id/fab_start_recording").click()
# #         self._device.delay(recordTimes)
#         self._logger.debug("Stop recording audio")
# #         self._device.click(705, 1930)
#         self._device.delay(1)
        self.add_and_delete_attachment("record")
        # if self._device(resourceId="com.google.android.apps.messaging:id/play_button").exists:
        #     self._device(resourceId="com.google.android.apps.messaging:id/close_button").click()
        #     self._device.delay(1)
        self.backToHomeFromMessage()
        return True

    def addAndDeleteAttachment(self):
        try:
            if self.slideAndPreviewMedia("image"):
                return True
        # if not self.enter_message():
        #     self.enter_message()
        # self.set_draft()
        # self._device(resourceId='com.google.android.apps.messaging:id/attach_media_button',\
        #                  descriptionContains="Add an attachment").click.wait()
        # self._device.delay(2)
        # for _ in range(5):
        #     if self._device(description="Explore more in Gallery").exists:
        #         self._device(description="Explore more in Gallery").click.wait()
        #         self._device.delay(2)
        #     if self._device(descriptionContains="Navigate up").exists and self._device(textContains="Gallery").exists:
        #         self._logger.debug("Enter gallary from message successfully!")
        #         break
        # attachmentType=["image","video"]
        # try:
        #     for addtypes in attachmentType:
        #         for _ in range(3):
        #             if self._device(resourceId="com.google.android.apps.messaging:id/gallery_content_async_image",descriptionContains=addtypes).exists:
        #                 self._device(resourceId="com.google.android.apps.messaging:id/gallery_content_async_image",descriptionContains=addtypes).click.wait()
        #                 self._device.delay(1)
        #                 break
        #             else:
        #                 self._device.swipe(240,1080,240,360,steps=50)
        #     if self._device(descriptionContains="Navigate up").exists:
        #         self._device(descriptionContains="Navigate up").click.wait()
        #         self._device.delay(2)
        #     for _ in range(3):
        #         if self._device(resourceId="com.google.android.apps.messaging:id/close_button").exists:
        #             self._device(resourceId="com.google.android.apps.messaging:id/close_button").click.wait()
        #             self._device.delay(1)
        #     if not self._device(resourceId="com.google.android.apps.messaging:id/close_button").exists:
        #         self._logger.info("Remove all attachment successfully.")
        #         return True
        #     self._logger.info("Remove all attachment fail.")
        #     return False
        except Exception:
                self.save_fail_img()
                self._logger.warning("addAndDeleteAttachment Exception!")
                common.log_traceback(traceback.format_exc())
                self.backToHome()
    

    def sharePicAndVideo(self):
        self._logger.debug("Launch gallery,sharePicAndVideo.")
        self._device.start_activity(gallery_package, gallery_activity)
        self._device.delay(2)
        # if not self._device(text="Photos").exists:
        #     return False
        # for _index in range(2):
        #     self._device(className="android.view.ViewGroup",instance=_index).long_touch()
        #     if self._device(resourceId="com.tclhz.gallery:id/moment_selection_menu_action_share").exists:
        #         break
        #     else:
        #         self._device(className="android.view.ViewGroup",instance=_index).long_touch()
        #     self._device.delay(1)
        # self._device(resourceId="com.tclhz.gallery:id/moment_selection_menu_action_share").click.wait()
        if self._device(resourceId="com.tclhz.gallery:id/comments_image_item").exists:
            self._device (resourceId="com.tclhz.gallery:id/comments_image_item").long_touch()
        if self._device(resourceId="com.tclhz.gallery:id/moment_selection_menu_action_share").exists:
            self._device (resourceId="com.tclhz.gallery:id/moment_selection_menu_action_share").click()
        self._device.delay(1)
        self.shareByMessage()
        self._logger.debug("SharePicAndVideo successful.")
        return True
 
        
    def shareByMessage(self,number="1111"):
        if self._device(text="Messages").exists:
            self._device(text="Messages").click.wait()
        self._device.delay(2)
        if self._device(text="New message").exists:
            self._device(text="New message").click.wait()
        self._device.delay(2)
        self._device(resourceId="com.google.android.apps.messaging:id/recipient_text_view").click()
        self._device(resourceId="com.google.android.apps.messaging:id/recipient_text_view").set_text(number)
        self._device.delay(1)
        self._device.press("enter")
        self._device.delay(1)
        if self._device(resourceId="com.google.android.apps.messaging:id/close_button").exists:
            self._device(resourceId="com.google.android.apps.messaging:id/close_button").click()
            self._device.delay(1)
        if self._device(resourceId="com.google.android.apps.messaging:id/compose_message_text").exists:
            self.backToHomeFromMessage()
            return True
        
    
    def shareRecording(self):
        self._logger.debug("Launch Sound Recorder,shareRecording.")
        self._device.start_activity(recorder_package, recorder_activity)
        self._device.delay(2)
        if not self._device(text="Sound Recorder").exists:
            return False    
        self._device(resourceId="com.tct.soundrecorder:id/file_list").click.wait()
        self._device.delay(1)
        self._device(resourceId="com.tct.soundrecorder:id/record_file_more",instance=0).click.wait()
        self._device.delay(1)
        self._device(text="Share").click()
        self._device.delay(1)
        self.shareByMessage()
        self.backToHome()
        self._logger.debug("Share Recording successful.")
        return True
    
    def shareContacts(self): 
        self._logger.debug("Launch Contacts,shareContacts.")
        self._device.start_activity(contact_package, contact_activity)
        self._device.delay(2)
        if not self._device(text="Contacts").exists:
            return False  
        lstItem = self._device(className="android.widget.ListView")
        lstItem.child(resourceId="com.tct.contacts:id/cliv_name_textview", instance=0).click()
        self._device.delay(1)
        self._device(description="More options").click.wait()
        self._device.delay(1)
        self._device(text="Share").click()
        self.shareByMessage()
        self._logger.debug("ShareContacts successful.")
        return True
    
    def shareDownloads(self):
        """The file size must less than 5M , or it won't be shared by message+"""
        self._logger.debug("Launch Downloads,shareDownloads.")
        self._device.start_activity(downloads_package, downloads_activity)
        self._device.delay(2)
        if self._device(description="Show roots").exists:
            self._device(description="Show roots").click.wait()
            self._device.delay(1)
        if not self._device(text="Downloads").exists:
            return False 
        self._device(text="Downloads").click.wait()
        self._device.delay(2)
        lstItem = self._device(resourceId="com.android.documentsui:id/dir_list")
        lstItem.child(className="android.widget.FrameLayout",instance=0).long_touch()
        self._device.delay(2)
        self._device(resourceId="com.android.documentsui:id/action_menu_share").click()
        self.shareByMessage()
        self.backToHome()
        self._logger.debug("shareDownloads successful.")
        return True        

    
if __name__ == "__main__":
    d = common.Device("GAWKFQT8WGL7L7S8")
    #d(resourceId="com.android.messaging:id/record_button_visual").long_touch(10)
    Msg=Message(d)
    #Msg.newAndsendMessage()
    #Msg.takePhotoFromMessage()
    #Msg.takeVideoFromMessage()
    #Msg.addAndDeleteAttachment()
    #Msg.sharePicAndVideo()
    #Msg.shareContacts()
    #Msg.shareRecording()
    #Msg.shareDownloads()
    Msg.slideAndPreviewMedia("video")