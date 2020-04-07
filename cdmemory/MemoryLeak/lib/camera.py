"""Camera library for scripts.
"""

import sys,re,subprocess
from lib import common
from lib.common import Common
PicPath = sys.path[0]+"\\ResourceFile\\PicComparison"
#StorePath_Media = '/storage/emulated/0/DCIM/Camera'
#StorePath_MessagePic = '/storage/emulated/0/DCIM/Message+'
camera_package = "com.tcl.camera"
camera_activity = "com.android.camera.CameraLauncher"

camera_2 = "com.google.android.packageinstaller"
setting_app_package=' com.android.settings'
setting_app_activity='.Settings'


class Camera(Common):  
    def __init__(self, device, log_name="CAMERA"):
        Common.__init__(self, device, log_name)
        
    def get_SDcard_name(self):   
        """get SD card folder name.
        """ 
        content = self._device.shell_adb('shell ls storage')
        res = re.search( r'.{4}-.{4}', content)
        if res:
            return res.group()
            #return res.group().decode('string_escape')
        else:
            self._logger.info("No SD Card in phone!")
            return '' 

        
    def enter_camera(self):      
        self._logger.debug('enter camera')
        self._device.start_activity(camera_package,camera_activity)
        self._device.delay(3)
        if self._device(textMatches="(?i)allow").exists:
            self._device(textMatches="(?i)allow").click.wait()
            self._device.delay(2)
        if self._device(resourceId="android:id/button1").exists:
            self._device(resourceId="android:id/button1").click()
            self._device.delay(2)
        if self._device.currentPackageName == camera_package:            
            self._logger.debug('enter camera successful!')
            return True
        self._logger.debug('enter camera fail!')
        return False
        
    def frontBackSwitch(self, picker="back"):
        pickerBtn = self._device(resourceId="com.tcl.camera:id/camera_toggle_button")
        if picker == 'back' and self._device(resourceId="com.tcl.camera:id/face_beauty_whiten_button").exists:    
            pickerBtn.click.wait()
            self._device.delay(3)
        elif picker == 'front' and not self._device(resourceId="com.tcl.camera:id/face_beauty_whiten_button").exists:
            pickerBtn.click.wait()
            self._device.delay(3)
    
    def switchScenario(self,scenario):
        self._logger.debug('switch scenario:'+scenario)
        self._device(text=scenario).click()
        self._device.delay(2)
        if self._device(text = "GOT IT").exists:
            self._device(text = "GOT IT").click()
            self._device.delay(2)
#         self._device.click(350,500)
        for _ in range(3):
            if self._device(resourceId ="com.tcl.camera:id/cancel_mode_selector").exists:
                self._device(resourceId ="com.tcl.camera:id/cancel_mode_selector").click.wait()
                self._device.delay(2)
            if self._device(resourceId = "com.tcl.camera:id/shutter_button").exists:
                break
        if self._device(resourceId = "com.tcl.camera:id/shutter_button").exists:
            self._device(resourceId = "com.tcl.camera:id/shutter_button").click()
        if self._device(resourceId = "com.mediatek.hz.camera:id/shutter_button_video").exists:
            self._device(resourceId = "com.mediatek.hz.camera:id/shutter_button_video").click()
        self._device.delay(4)
          
        if scenario == "PORTRAIT":
            if self._device(resourceId = "com.tcl.camera:id/shutter_button").exists:
                self._device(resourceId = "com.tcl.camera:id/shutter_button").click()
            self._device.delay(2)
        elif scenario == 'WIDE':
            self._device.delay(5)
#             self._device.click(350,500)
            self._device(resourceId = "com.tcl.camera:id/shutter_button").click()
            self._device.delay(2)
        return True
        
    def take_photo(self, picker="back"):        
        self._logger.debug('take photo')
        if self._device(resourceId="com.tcl.camera:id/face_beauty_whiten_button").exists:
            self._device(resourceId="com.tcl.camera:id/camera_toggle_button").click.wait()
        self.frontBackSwitch(picker)
        # StorePath_Media = '/storage/'+self.get_SDcard_name()+'/DCIM/Camera'
        StorePath_Media = '/sdcard/'+ '/DCIM/Camera'
        file_number = self.get_file_num(StorePath_Media,".jpg")
        if self._device(text = "AUTO").exists:
            self._device(text = "AUTO").click()
        if self._device(description = "AUTO").exists:
            self._device(description = "AUTO").click()
        if self._device(text = "Auto").exists:
            self._device(text = "Auto").click()
        self._device.delay(2)
        if self._device(resourceId='com.tcl.camera:id/shutter_button').exists:
            self._device(resourceId='com.tcl.camera:id/shutter_button').click()
        self._device.delay(10)
#         if self._device(resourceId="com.tct.camera:id/button_done").exists:
#             self._device(resourceId="com.tct.camera:id/button_done").click()
#             self._device.delay(1)       
        if (self.get_file_num(StorePath_Media,".jpg") > file_number) and self.preview_del(".jpg"):
            return True
        else:
            self._logger.warning("Take picture failed!")
            return False

    def preview(self):
        self._logger.debug('enter preview mode')
        for _ in range(3):
            if self._device(resourceId = 'com.tclhz.gallery:id/media_item_view_video_play').exists:
                break
            else:
                self._device(resourceId="com.tcl.camera:id/peek_thumb").click.wait()
                self._device.delay(3)
            if self._device(resourceId="com.android.packageinstaller:id/permission_allow_button").exists:
                self._device(resourceId="com.android.packageinstaller:id/permission_allow_button").click.wait()
                self._device.delay(2)
            if self._device(text = 'Gallery').exists:
                self._device(text = 'Gallery').click.wait()
                self._device.delay(1)
            if self._device(resourceId = 'android:id/button_always').exists:
                self._device(resourceId = 'android:id/button_always').click.wait()
                self._device.delay(2)
        if self._device(resourceId = 'com.tclhz.gallery:id/media_item_view_video_play').exists:
            self._logger.debug('enter preview mode success')
            return True
        self._logger.debug('enter preview mode fail')
        return False
    
    def backToCamera(self):
        for _ in range(5):
            if self._device(resourceId='com.tcl.camera:id/shutter_button').exists:
                break
            self._device.press("back")
            self._device.delay(1)
        else:
            self.backToHome()
            self.enter_camera()    
    
    def takeVideo(self, picker="back"):
        self._logger.debug('take video')
        self.frontBackSwitch(picker)
        if not self._device(resourceId="com.tcl.camera:id/onscreen_mute_sound").exists:
            self._device(resourceId="com.tcl.camera:id/photo_video_change").click.wait()
        if self.record_video(120) and self.playVedio(60) and self.preview_del(".mp4"):
            self._logger.debug('take video successful')
            return True
        self._logger.debug('take video fail')
        return False
               
    def preview_del(self, _format=".jpg"):  
        self._logger.info("Delete %s file" % _format)
#         self.preview()
#         StorePath_Media = '/storage/'+self.get_SDcard_name()+'/DCIM/Camera'
        StorePath_Media = '/sdcard/' + '/DCIM/Camera'
        file_number = self.get_file_num(StorePath_Media, _format)
        self._device.delay(1)
        # path = self.get_SDcard_name()
        # self._device.shell_adb("shell rm -rf /sdcard/"+path+"/DCIM/Camera/*")
        self._device.shell_adb ("shell rm -rf /sdcard/"+"/DCIM/Camera/*")
#         for _ in range(3):
#             if self._device(resourceId = 'com.google.android.apps.photos:id/trash').exists: 
#                 self._device(resourceId = 'com.google.android.apps.photos:id/trash').click.wait()
#                 break
#             else:   
#                 self._device.click(self._device.displayWidth/2-100, self._device.displayHeight/2-100) 
#                 self._device.delay(0.5)
#         if self._device(resourceId = 'android:id/button1').exists: 
#             self._device(resourceId = 'android:id/button1').click.wait()
#             self._device.delay(3)
#         if self._device(resourceId = 'com.google.android.apps.photos:id/move_to_trash').exists: 
#             self._device(resourceId = 'com.google.android.apps.photos:id/move_to_trash').click.wait()
#             self._device.delay(3)
#         if self._device(text="Allow").exists:
#             self._device(text="Allow").click()
#             self._device.delay(3)
#         if self._device(text="ALLOW").exists:
#             self._device(text="ALLOW").click()
#             self._device.delay(5)
#         if self._device(text="Delete item permanently?").exists:
#             self._device(text="DELETE PERMANENTLY").click()
#             self._device.delay(5)
        for _ in range(10): 
            if self.get_file_num(StorePath_Media, _format) < file_number:
                self._logger.info("Delete file from preview successful") 
                return True
            self._device.delay(5)
        self.backToCamera()
        self._logger.warning("delete file failed!")
        return False
       
    def record_video(self, recordTime):
        self._logger.debug('record video')
        # StorePath_Media = '/storage/'+self.get_SDcard_name()+'/DCIM/Camera'
        StorePath_Media = '/sdcard/' + '/DCIM/Camera'
        file_number = self.get_file_num(StorePath_Media,".mp4")
        if self._device(resourceId='com.tcl.camera:id/shutter_button').exists:
            self._device(resourceId='com.tcl.camera:id/shutter_button').click()
            self._device.delay(recordTime)
        self._device(resourceId='com.tcl.camera:id/shutter_button').click()
        self._device.delay(6)
        if self.get_file_num(StorePath_Media,".mp4") > file_number:
            return True
        else:
            self._logger.warning("Record video failed!")
            return False
        
    def playVedio(self, playtime=5):
        self._logger.debug('play video')
        self.preview()
        for _ in range(3):
            if self._device(resourceId="com.tclhz.gallery:id/media_item_view_video_play").exists:
                self._device(resourceId="com.tclhz.gallery:id/media_item_view_video_play").click.wait()
                break
            self._device.click(255,488)
            self._device.delay(2)
#         for _ in range(2):
#             self._device.click(self._device.displayWidth/2, self._device.displayHeight/2)        
#             self._device.delay(1)
        if  self._device(text='Video player').exists:
            self._device(text='Video player').click()
            self._device.delay(1)
        if self._device(text='Always').exists:
            self._device(text='Always').click()
            self._device.delay(2)
        if  self._device(text='GOT IT').exists:
            self._device(text='GOT IT').click()
            self._device.delay(1)
        self._device.delay(playtime)
        flag = False
        out = self._device.shell_adb("shell dumpsys media.player")
        if out.find("state(5)") > -1:
            self._logger.debug('play video successful')
            flag = True
#         self._device.click(240,720)
#         self._device.delay(2)
#         if self._device(resourceId="com.google.android.apps.photos:id/photos_videoplayer_pause_button").exists:
#             self._logger.debug("Play video successfully")
#             flag = True
        self._device.press('back')
        self._device.delay(2)
        return flag
    
    def reEnterCamera(self):
        if self.enter_camera():
            self.backToHome()
            return True
        
        return False
    
    def enterCameraByRecent(self):
        self._logger.debug('enter Camera By Recent')
        if self.enter_camera():
            self.backToHome()
            if self.task_enter():
                if self._device(resourceId="com.android.launcher3:id/snapshot").exists:
                    self._device(resourceId="com.android.launcher3:id/snapshot").click.wait() 
#                 if self._device(text="Camera").exists:
#                     self._device(text="Camera").click()  
                    self._device.delay(2)
                    if self._device.currentPackageName == camera_package:
                        return True
        return False
    
    def burstShot(self):
#         self.frontBackSwitch("back")
#         StorePath_Media = '/storage/'+self.get_SDcard_name()+'/DCIM/Camera'
        StorePath_Media = '/sdcard/'+'/DCIM/Camera'
        file_number = self.get_file_num(StorePath_Media,".jpg")
        if self._device(text = "AUTO").exists:
            self._device(text = "AUTO").click()
        elif self._device(text = "Auto").exists:
            self._device(text = "Auto").click()
        self._device.delay(3)
        if self._device(resourceId = "com.tcl.camera:id/shutter_button").exists: 
            self._device(resourceId = "com.tcl.camera:id/shutter_button").click()
            self._device.delay(3)
        self._device(descriptionStartsWith='Shutter').long_touch(5)
        self._device.delay(30)
        for _ in range(4):
            if self.get_file_num(StorePath_Media,".jpg") > file_number:
                break
            else:
                self._device.delay(5)
        if (self.get_file_num(StorePath_Media,".jpg") > file_number) and self.preview_del(".jpg"):
            self._logger.info("Take picture success!")
            return True
        else:
            self._logger.warning("Take picture failed!")
            

if __name__ == "__main__":
    d = common.Device("501b68d4")
    cam = Camera(d)
    t=cam.get_SDcard_name()
    print(t)
    
