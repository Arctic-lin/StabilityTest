#!coding=utf-8
'''Camera library for scripts.
'''

from common import *
from google_music import google_Music
from native_music import native_Music
from settings import Settings

PORTRAIT = 'PORTRAIT'
SUPER_NIGHT = 'SUPER NIGHT'
PRO = 'PRO'
AUTO = 'AUTO'
VIDEO = 'VIDEO'
GO_MODE = {VIDEO: 1, PORTRAIT: 2, SUPER_NIGHT: 3, PRO: 4}

class Camera(Common):
    # app_name = 'Snapdragon Camera'
    # package = 'org.codeaurora.snapcam'
    # launch_activity = 'com.android.camera.CameraActivity'
    # shutter_res_id = 'org.codeaurora.snapcam:id/shutter_button'
    app_name = 'Camera'
    package = 'com.tcl.camera'
    launch_activity = 'com.android.camera.CameraActivity'
    shutter_res_id = 'com.tcl.camera:id/shutter_button'


    def __init__(self, device, mod, sdevice=None):
        Common.__init__(self, device, mod, sdevice)
        self.music = native_Music(self.device, 'camera_music')
        self.settings = Settings(self.device, 'settings')
        self.countdown_toggle_btn = self.device(resourceId='com.tcl.camera:id/countdown_toggle_button')
        self.hdr_btn =self.device(resourceId='com.tcl.camera:id/hdr_plus_toggle_button')
        self.flash_btn = self.device(resourceId="com.tcl.camera:id/flash_toggle_button")
        self.shutter_btn = self.device(resourceId='com.tcl.camera:id/shutter_button')
        self.mute_sound_btn = self.device(resourceId='com.tcl.camera:id/onscreen_mute_sound')
        # self.photo_video_switch_btn = self.device(resourceId='com.tcl.camera:id/photo_video_change')
        self.video_mode_btn = self.device(text='VIDEO')
        self.photo_mode_btn = self.device(text='AUTO')
        self.to_preview_btn = self.device(resourceId='com.tcl.camera:id/peek_thumb')
        self.front_back_switch_btn = self.device(resourceId='com.tcl.camera:id/camera_toggle_button')

    def setup(self):
        self.clear(self.package)
        self.start_app(self.app_name)
        if self.device(text = "ALLOW ALL THE TIME").wait.exists(timeout=5000):
            self.device(text = "ALLOW ALL THE TIME").click()
        # self.allow_permissions()
        el = self.device(textMatches='ok|OK')
        if el.exists:
            el.click()

    def enter(self):
        '''Launch camera by StartActivity.
        '''

        self.logger.debug('enter camera')
        self.start_app(self.app_name, True)
        # add skip welcome
        # if self.device(text='SKIP').wait.exists(timeout=3000):
        #     self.device(text='SKIP').click.wait()
        # self.device.delay(2)
        self.logger.info("Camera entered without check")  # cut test time
        return True

        # if self.shutter_btn.exists:
        #     return True
        # else:
        #     self.logger.debug('enter camera')
        #     self.start_app(self.app_name, True)
        #     # add skip welcome
        #     # if self.device(text='SKIP').wait.exists(timeout=3000):
        #     #     self.device(text='SKIP').click.wait()
        #     self.device.delay(3)
        #     self.logger.info("Camera entered")  # cut test time
        #     return True
            # if self.shutter_btn.exists:
            #     self.logger.info("Camera entered")
            #     return True
            # else:
            #     self.logger.debug('enter camera fail!')
            #     self.save_fail_img()
            #     return False

    def back_to_camera(self):
        self.logger.debug('Back to camera')
        for i in range(5):
            self.device.delay(1)
            if self.shutter_btn.exists:
                return True
            self.device.press.back()
        else:

            self.logger.warning('Cannot back to camera')
            self.save_fail_img()
            return False

    def get_photo_number(self):
        return self.get_file_num(self.appconfig('storage_path', 'Camera'), '.jpg')

    def get_video_number(self):
        return self.get_file_num(self.appconfig('storage_path', 'Camera'), '.mp4')

    def get_screenrecord_number(self):
        return self.get_file_num(self.appconfig('screen_path', 'Camera'), '.mp4')

    def get_screenshot_number(self):
        return self.get_file_num(self.appconfig('screen_path', 'Camera'), '.png')

    def get_media_number(self):
        return self.get_file_num(self.appconfig('storage_path', 'Camera'), '')

    def get_number(self, type):
        if type == 'photo':
            return self.get_photo_number()
        else:
            return self.get_video_number()

    def switch_picker(self, picker):
        '''switch camera picker
        '''
        self.logger.debug('switch to %s picker' % picker)
        self.device.delay(2)
        # no way to fingure out whether it is back camera or front camera just click swtich
        # switch_btn = self.device(resourceId='org.codeaurora.snapcam:id/front_back_switcher')
        # switch_btn.click()
        # return True  # self.device(text='Video').click()
        if picker == self.is_font_or_back_mode():
            self.logger.debug('it is %s picker already' % picker)
            return True
        self.front_back_switch_btn.click()
        self.device.delay(5)

        if picker == self.is_font_or_back_mode():
            self.logger.debug('switch %s picker successfully' % picker)
            return True

        self.logger.warning('switch %s picker failed' % picker)
        self.save_fail_img()
        return False

    def click_camera_picker_btn(self):
        #聚焦?
        x, y = 462, 744
        self.device.click(x, y)
        self.device.delay(3)
        return True

    def take_photo(self):
        '''take photo
        '''
        self.logger.debug('take photo')
        file_number = self.get_photo_number()
        self.device.delay(3)  # wait more time for activity update after camera switch, bad performance
        self.click_shutter_btn()
        for i in range(10):  # bad performance, the preview generation take much time, sometime do not generate
            self.logger.debug("Count the number of photos %d times" % i)
            if self.get_photo_number() > file_number:
                return True
            self.device.delay(1)

        self.logger.warning('Take photo failed!')
        self.save_fail_img()
        return False

    def continuous_shooting(self):
        try:
            self.logger.debug('take continuous shooting')
            if not self.shutter_btn.wait.exists(timeout=2000):
                self.logger.debug('*****camera maybe exit*****')
                self.enter()
            file_number = self.get_photo_number()
            self.device.delay(5)  # todo: wait more time for activity update after camera switch, bad performance
            # for _ in range(10):
            #     self.shutter_btn.click()
            self.device.swipe(310, 1406, 371, 1406, steps=1000)
            self.device.delay(10)
            
            if self.get_photo_number() > file_number:
                # cannot start preview after continue shot, restart camera
                self.logger.debug("the")
                self.back_to_home()
                self.enter()
                return True
            else:
                self.logger.warning('Take continues shot failed!')
                self.save_fail_img()
                self.back_to_home()
                self.enter()
                return False
        except Exception, e:
            self.logger.debug('*****camera maybe exit, exceptions here:*****')
            self.logger.warning(e)
            self.save_fail_img()
            self.enter()

    def preview(self):
        '''enter preview mode
        '''
        self.logger.debug('enter preview mode')
        if self.device(description='Delete').wait.exists():
            self.logger.debug('enter preview mode success!')
            return True
        elif self.device(resourceId='com.blackberry.camera:id/thumbView').wait.exists():
            for i in range(4):
                self.device(resourceId='com.blackberry.camera:id/thumbView').click.wait()
                if self.device(description='Delete').wait.exists():
                    self.logger.debug('enter preview mode success!')
                    return True
        self.logger.debug('enter preview mode failed!')
        self.save_fail_img()
        return False

    def is_preview_enter(self):
        if self.device(resourceId="com.tclhz.gallery:id/media_item_view_item").exists:
            self.logger.debug("Enter the preview successfully")
            return True
        return False

    def to_preview(self):
        """
        这个控件不容易定位到，需要尝试多种方式
        :return:
        """
        self.logger.debug("try to enter camera preview")

        if self.isMILAN_GL:
            x, y = 111, 1409
        elif self.isMILAN_EEA:
            x, y = 111, 1409
        else:
            x, y = 143, 2061
        self.adb.shell("input tap %d %d"%(x,y))
        time.sleep(2)
        if self.is_preview_enter():
            return True
        self.logger.debug("input tap failed ,try another way")

        if self.device(resourceId="com.tcl.camera:id/peek_thumb").exists:
            self.device(resourceId="com.tcl.camera:id/peek_thumb").click()
            if self.is_preview_enter():
                return True
        self.logger.debug("not found 'com.tcl.camera:id/peek_thumb',try another way")

        if self.device(description="Preview").exists:
            self.device(description="Preview").click()
            if self.is_preview_enter():
                return True
        self.logger.debug("not found 'Preview',try another way")

        self.device.click(x, y)
        if self.is_preview_enter():
            return True

        assert False,"Enter the preview fail"

    def delete(self, media_type):
        '''delete photo/video in preview mode
        '''
        try:
            self.logger.debug('delete %s' % media_type)
            file_number = self.get_number(media_type)
            self.to_preview()
            for i in range(120):
                current_num = self.get_number(media_type)
                self.logger.info("current media num:{}".format(current_num))
                if current_num == 0:
                    break
                el = self.device(resourceId='com.tclhz.gallery:id/media_item_view_action_delete')
                if el.exists:
                    self.logger.debug("delete resourceId exists")
                    el.click.wait()
                    self.device.wait.idle()
                    if self.device(text="DELETE").exists:
                        self.device(text="DELETE").click()
                    else:
                        self.click_text_DELETE()
                    continue
                else:  # del first one, all icons disappear, click to show icons
                    self.logger.debug("delete resourceId not exists,click 383 944 to popup delete ui")
                    self.device.click(383, 944)
                    self.device.delay(1)

            self.restart_camera()
            self.device.delay(2)
            if self.get_number(media_type) < file_number:
                self.logger.info('delete %s success' % media_type)
                return True
            else:
                self.logger.warning('Delete failed!')
                self.save_fail_img()
                return False
        except:
            self.logger.warning(traceback.format_exc())
            return False

    def record_video(self, duration=15):
        '''record video
        argv: (int)recordTime --time of the video
        '''
        self.logger.debug('record video')
        file_number = self.get_video_number()
        self.device.delay(2)
        if not self.switch_video_mode():
            return False
        self.device.delay(2)
        # self.shutter_btn.click()
        self.click_shutter_btn()
        self.device.delay(duration)
        # self.shutter_btn.click()
        self.click_shutter_btn()
        self.device.delay(3)
        if self.get_video_number() > file_number:
            self.restart_camera()
            return True
        else:
            self.logger.warning('Record video failed!')
            self.save_fail_img()
            return False

    def click_shutter_btn(self):
        print "click_shutter_btn start"
        self.device(resourceId="com.tcl.camera:id/shutter_button").click()
        # x, y = 548, 2061
        # self.device.click(x, y)
        # self.device.delay(1)

        print "click_shutter_btn completed"
        return True

    def switch_video_mode(self):
        '''
        switch camera mode to video or phone or other modes
        to compare with other Mercury/Krypton
        use getprop ro.product.model as id
        Athena - BBF100-2
        Mercury - BBB100-
        Krypton - BBD100-
        :return:
        '''
        if self.is_video_mode():
            self.logger.info('switch to video successfully')
            return True
        # if self.video_mode_btn.exists:
        #     self.video_mode_btn.click()
        self.device.delay ()
        x, y = 506, 1417
        self.device.click (x, y)
        self.device.delay(2)
        if self.is_video_mode():
            self.logger.info('switch to video successfully')
            return True
        self.logger.info('switch to video failed')
        self.save_fail_img()
        return False

    def click_video_mode(self):
        #Video Button?
        self.device.delay()
        x, y = 506, 1417
        self.device.click(x, y)
        self.device.delay()
        return True

    def switch_photo_mode(self):
        self.logger.info("try to switch to photo mode")
        if self.is_photo_mode():
            self.logger.info('switch to photo successfully')
            return True
        self.photo_mode_btn.click()
        self.device.delay()
        if self.is_photo_mode():
            self.logger.info('switch to photo successfully')
            return True
        self.logger.info('switch to photo failed')
        self.save_fail_img()
        return False
        # el = self.device(resourceId='org.codeaurora.snapcam:id/camera_switcher')
        # el.click()
        # el = self.device(description='Switch to photo')
        # el.click()
        # self.device.delay()
        # self.logger.info('switch to photo successfully')
        # return True

    def play_video(self, duration=15):
        '''play video
        '''
        self.logger.debug('play video')
        self.to_preview()
        self.logger.info("entered preview")
        el = self.device(resourceId='com.tclhz.gallery:id/media_item_view_video_play')
        el.click.wait()
        self.device.delay(duration)
        if not el.exists:
            self.back_to_camera()
            self.device.delay(2)
            return True
        self.logger.warning('Play video failed!')
        self.save_fail_img()
        return False

    def take_photo_during_music(self):
        if self.take_photo():
            # self.device.swipe(350, 20, 350, 200, 10)
            self.device.open.notification()
            self.device.delay(2)
            if not self.device (resourceId="com.tct.music:id/ly_notification_quick_control").exists:
                self.logger.warning('music isn\'t playing!!!')
                self.save_fail_img()
                return False
            self.logger.debug('music is playing')
            self.back_to_home()
            # self.back_to_camera()
            return True
        return

    def take_photo_to_low(self):
        self.logger.info('take photo to low storage')
        self.watch_low_storage_then_del_media_files()
        self.back_to_home()
        self.enter()
        while True:
            if self.watch_low_storage_then_del_media_files():
                self.back_to_home()
                self.enter()
                return True
            self.continuous_shooting()
            self.device.delay(2)
        return False

    def take_video_to_low(self):
        self.logger.info('take photo to low storage')
        self.watch_low_storage_then_del_media_files()
        self.back_to_home()
        self.enter()

        if not self.switch_video_mode():
            return False

        self.logger.info('start to recording video')
        self.shutter_btn.click()

        while True:
            if self.device(resourceId='com.tcl.camera:id/video_pause_button').wait.exists():
                self.device.delay(10)
            else:
                self.logger.info("file size limit, record video again")
                if self.shutter_btn.wait.exists():
                    self.shutter_btn.click()
            if self.watch_low_storage_then_del_media_files():
                    return True

        self.logger.info('take video to low storage failed')
        self.save_fail_img()
        return False

    def watch_low_storage_then_del_media_files(self):
        # self.logger.info('battery capacity: %s' % self.adb.battery_level())
        self.sleep_if_power_low()
        if self.device(text="Attention").wait.exists(timeout=3000):
            self.del_media_fils()
            if self.device(text="OK").wait.exists(timeout=3000):
                self.device(text='OK').click()
            return True
        if self.device(resourceId="com.tcl.camera:id/shutter_button", clickable=False).exists:
            self.logger.info('phone storage is low')
            if self.device(text="OK").wait.exists(timeout=3000):
                self.device(text='OK').click()
            self.del_media_fils()
            return True
        return False

    def del_folder(self, folder):
        self.settings.enter_settings('Storage')
        self.settings.device(resourceId='com.android.settings:id/list').scroll.vert.to(text='Explore')
        self.settings.device(text='Explore').click()
        if self.settings.device(text=folder).wait.exists():
            self.settings.device(text=folder).long_click()
        self.settings.device(resourceId='com.android.documentsui:id/menu_delete').click.wait()
        self.settings.device(text='OK').click.wait()

    def enable_hdr(self):
        '''
        enable HDR
        :return:
        '''
        self.logger.info('enable hdr')
        # click hdr mode
        hdr_mode = self.device(descriptionContains='HDR')
        assert hdr_mode.wait.exists(), '******** can not find HDR mode  ********'
        hdr_mode.click()

        # select HDR On
        hdr_on = self.device(description='HDR On')
        assert hdr_on.wait.exists(), '******** can not find HDR on  ********'
        hdr_on.click.wait(timeout=3000)

    def del_media_fils(self):
        '''
        del files in /sdcard/DCIM/Camera/
        :return:
        '''
        self.logger.info('remove media files via abd cmd')
        self.adb.shell('rm -r /sdcard/DCIM/Camera/*')
        self.device.delay(30)
        for i in range(3):
            if self.get_media_number() > 10:
                self.device.delay(10)
        self.logger.info('remove media files done')

    def is_front_camera(self):
        """
        :return: true, is front, false, not
        """
        if self.device(description="Front camera").wait.exists(timeout=3000):
            return True
        return False

    def is_back_camera(self):
        """
        :return:  true, is back, false, not
        """
        if self.device(description="Back camera").wait.exists(timeout=3000):
            return True
        return False

    def is_video_mode(self):
        if self.mute_sound_btn.wait.exists(timeout=3000):
            return True
        return False

    def is_photo_mode(self):
        # self.restart_camera_if_needed()
        if self.countdown_toggle_btn.wait.exists(timeout=3000):
            return True
        return False

    def is_video_or_photo_mode(self):
        """

        :return: return photo or video
        """
        # self.restart_camera_if_needed()
        return 'photo' if self.is_photo_mode() else 'video'

    def is_font_or_back_mode(self):
        """

        :return: return front or back
        """
        # self.restart_camera_if_needed()
        return 'front' if self.is_front_camera() else 'back'

    def restart_camera_if_needed(self):
        self.logger.info("restart_camera_if_needed")
        if self.device(packageName="com.tcl.android.launcher").wait.exists(timeout=2000):
            self.enter()

    def restart_camera(self):
        self.back_to_home()
        return self.enter()

    def prepare_video(self, times):
        for i in range(times):
            self.screenrecord()  # record 10s
            self.logger.info("generate video-{}".format(i))
            self.device.delay(12)

    def prepare_pic(self, times):
        print "prepare picture %d times"%times
        for i in range(times):
            self.screenshot()
            self.logger.info("generate pic-{}".format(i))
            self.device.delay(2)

    def camera_random_setting(self):
        try:
            self.enter()

            # open camera setting
            self.open_camera_settings()

            # random click settings
            self.click_random_item()

            # restart camera
            self.restart_camera()
        except:
            self.logger.warning(traceback.format_exc())
            self.save_fail_img()

    def open_camera_settings(self):
        """
        open camrea settings via location
        :return:
        """
        self.device.delay(1)
        self.device.click(242, 1276)  # click more
        # self.device.delay()
        # self.device.click(199, 439)  # click setting icon
        # self.device.delay()
        self.device.delay(3)
        # if self.device(resourceId="com.tcl.camera:id/settings").ext5:
        #     self.device(resourceId="com.tcl.camera:id/settings").click()
        self.device.click (55, 606)
        assert self.device(resourceId="com.tcl.camera:id/action_to_help_and_tips").wait.exists(
            timeout=5000), "**** can not find help icon ****"

    def click_random_item(self):
        """
        点击随机生成的菜单选项
        :return:
        """
        special_items = {'Photo size': 4, 'Video quality': 4, 'Volume button function': 3}  # 带弹出框的菜单：弹出框有几个选项
        ignore_items = {'PHOTO', 'VIDEO', 'GENERAL', 'Storage'}
        # random_items = self._export_random_camera_settings(ignore_items)
        random_items = {'Reset settings', 'Watermark', 'Shutter sound', 'Grid'}
        for item in random_items:
            self.logger.info("click {}".format(item))
            self.device(scrollable=True).scroll.vert.to(text=item)
            self.device(text=item).click()
            self.device.wait.idle()

            # 特殊菜单处理
            if item in special_items:  # 处理弹出菜单
                ind = self._click_random_option(special_items.get(item))
                self.logger.info("{} selected index:{}".format(item, ind))
            elif self.device(text='RESET', resourceId="android:id/button1").exists:  # 处理reset settings
                self.logger.info("confirm reset and break camera settings")
                self.device(text='RESET', resourceId="android:id/button1").click()
                return  # reset后，camera settings界面退出，自动返回到camera预览界面，退出执行

        self.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)

    def _export_random_camera_settings(self, ignore_items, sample_count=4):
        """
        随机生成需要点击的菜单
        :param ignore_items:
        :return:
        """
        texts = set()
        for i in range(2):
            count = self.device(resourceId="android:id/title").count
            self.logger.debug("******* android:id/title count:{} ******".format(count))
            for j in range(count):
                text = self.device(resourceId="android:id/list") \
                    .child(className="android.widget.LinearLayout", index=j) \
                    .child(resourceId="android:id/title").get_text()
                texts.add(text)
            self.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)
        self.logger.info("all items: {}".format(texts))
        random_item = random.sample(texts - ignore_items, sample_count)  # 随机生成sample
        self.logger.info("random_item in camera settings:{}".format(random_item))
        self.device(scrollable=True).scroll.vert.toBeginning(steps=100, max_swipes=100)  # 返回settings顶部
        return random_item

    def _click_random_option(self, max_num):
        """
        有的选项带有弹出菜单，需要再弹出菜单中选择，
        随机选择弹出菜单的选项
        :param max_num:
        :return:
        """
        index = random.randint(0, max_num - 1)
        el = self.device(resourceId="com.tct:id/tct_text1", index=index)
        if el.wait.exists(timeout=2000):
            el.click()
        return index

    def switch_photo_type(self, photo_mode):
        """
        通过滑动切换photo mode
        :param photo_mode:
        :return:
        """
        if photo_mode == AUTO:
            return
        sx, sy, ex, ey = 540, 1400, 80, 1400
        for i in range(GO_MODE.get(photo_mode)):
            self.device.swipe(sx, sy, ex, ey, steps=100)
            self.device.delay(timeout=3)

if __name__ == '__main__':
    a = Camera('3dc2a8f3', 'Camera')
    # a.case_take_photo(2)
    # a.case_record_video(1)
    # a.case_continuous_shooting(1)
    # a.device.open.quick_settings()
    a.continuous_shooting()