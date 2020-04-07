#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2018/9/11 14:19

information about this file
"""
from common import *


class Gallery(Common):
    def __init__(self, device, mod, sdevice=None):
        Common.__init__(self, device, mod, sdevice)
        # self.tab_photos = self.device(
        #     resourceId="com.google.android.apps.photos:id/tab_photos")  # help to ensure photo home activity
        # self.tab_albums = self.device(resourceId="com.google.android.apps.photos:id/tab_albums")
        self.top_tab = self.device(resourceId="com.tclhz.gallery:id/viewpagertab")  # index for Gallery home activity
        self.media_file_item = self.device(resourceId="com.tclhz.gallery:id/comments_image_item")
        self.play = self.device(resourceId="com.tclhz.gallery:id/media_item_view_video_play")

    def enter(self):
        """Launch gallery by StartActivity.
        """

        if self.top_tab.exists:
            self.logger.debug('Gallery opened already')
            return True
        else:
            self.logger.debug('enter Gallery')
            self.start_app("Gallery")  # it is Photos for GL Blackberry devices
            # add skip welcome
            if self.top_tab.wait.exists(timeout=8000):
                return True
            else:
                self.logger.debug('enter Gallery fail!')
                self.save_fail_img()
                return False

    def open_file(self, video=False, index=1):
        # des_file = 'Video taken on' if video else 'Photo taken on'
        # f = self.device(descriptionStartsWith=des_file, index=index)
        # assert f.wait.exists(), "**** can not find file(%s, %s) ****" % (des_file, index)
        # f.click.wait(timeout=3000)
        #
        # assert not self.tab_photos.wait.exists(timeout=1500), "**** file do not opened ****"
        self.media_file_item.click.wait()
        assert not self.top_tab.wait.exists(timeout=1500), "**** file do not opened ****"

    def swipe_file(self, sx, sy, ex, ey, steps=10, video=False):
        # self.device.wait.idle()  # can not use wait idle when video playing, it will always waiting
        self.device.delay(2)
        if video:
            assert self.verify_video_playing(), 'verify video playing fail'
        # remove verify function, when swipe the menu icon will disappear, can not control
        # ret1 = self.get_file_detail_name()
        # self.logger.info('before: ' + ret1)
        self.device.delay(1)
        self.device.swipe(sx, sy, ex, ey, steps)
        self.device.delay(1)
        # self.logger.debug("******* swiped ******")
        # ret2 = self.get_file_detail_name()
        # self.logger.info('after: ' + ret2)

        # assert ret1 != ret2, "swipe fail"
        self.logger.info('swipe success')
        return True

    def show_menu(self):
        menu = self.device(resourceId="com.tclhz.gallery:id/media_item_view_action_popup_menu")
        if not menu.wait.exists():  # play first video from photos, the video will auto play, click to active menu
            self.device.click(500, 500)
        assert menu.wait.exists(), "**** can not find menu ****"
        menu.click.wait(timeout=1000)
        self.device.delay(1)

    def open_menu_item(self, text):
        self.show_menu()
        item = self.device(text=text)
        assert item.wait.exists(), "**** can not find %s ****" % text
        item.click.wait(timeout=3000)

    def get_file_detail_name(self):
        self.open_menu_item('Details')
        text = self.device(textStartsWith="Path:").get_text()
        self.device.press.back()
        return text

    def del_file(self):
        ret1 = self.get_file_detail_name()
        self.logger.info('before: ' + ret1)
        self.device.wait.idle()

        delbtn = self.device(resourceId="com.tclhz.gallery:id/media_item_view_action_delete")
        # assert delbtn.wait.exists(), "**** can not find trash icon ****"
        if not delbtn.exists:  # 有的时候进入到全屏浏览界面，点击屏幕, 避开play，显示所有icon
            self.logger.info("can not find del btn, click screen to show it")
            self.device.click(364, 468)
            self.device.delay(2)
        if delbtn.wait.exists():
            delbtn.click()

        # move_msg = self.device(text="DELETE")
        # if move_msg.wait.exists(timeout=3000):
        #     move_msg.click.wait()
        self.device.delay(2)
        self.click_text_DELETE()
        self.device.delay(2)  # add 2s for bad performance

        if self.is_no_files_in_gallery():
            self.logger.info('the last file delete success')
            return True

        # 876, 1448, bug，删除第一张照片后，再次点击menu，menu会显示异常
        self._show_menu_again()

        ret2 = self.get_file_detail_name()
        self.logger.info('after: ' + ret2)

        if ret1 != ret2:
            self.logger.info('delete success')
            return True
        self.logger.info('delete fail')
        return False

    def del_file_without_check(self):
        self.logger.debug("start to del_file_without_check")
        delbtn = self.device(resourceId="com.tclhz.gallery:id/media_item_view_action_delete")
        if delbtn.wait.exists():
            self.logger.debug("found delbtn")
            delbtn.click()
        else:
            if self.device(text="No photos").exists:
                self.logger.debug("found No photos,delete all pic/video successfully")
                return True
            # 有的时候进入到全屏浏览界面，点击屏幕, 避开play，显示所有icon
            self.logger.info("can not find del btn, click screen to show it")
            self.device.click(364, 468)
            if delbtn.wait.exists():
                delbtn.click()
            self.device.delay(0.5)

        self.click_text_DELETE()
        self.device.wait.idle()
        if self.is_no_files_in_gallery():
            self.logger.info('the last file delete success')
            return True
        # 876, 1448, bug，删除第一张照片后，再次点击menu，menu会显示异常
        self._show_menu_again()
        self.logger.info('delete picuure without check successfully')
        return True

    def _show_menu_again(self):
        x, y = 876, 1448
        self.device.delay(1)
        self.device.click(x, y)
        self.device.delay(2)
        self.device.click(x, y)
        self.device.delay(2)

    def verify_video_playing(self, play_time=16):
        """
        assume video limit is 15
        :param play_time:
        :return:
        """
        assert self.play.wait.exists(), "**** can not find play btn ****"
        self.play.click.wait(timeout=3000)
        # self.logger.debug("******* play btn clicked ******")
        self.device.delay(timeout=play_time)
        # self.device.press.back()
        if not self.play.exists:
            return True
        return False

    def del_mediafiles_in_gallery(self):
        """
        del media file in gallery one by one
        :return:
        """
        self.logger.info("try to del all media files")
        media_item = self.device(resourceId="com.tclhz.gallery:id/comments_image_item")

        for i in range(10):
            self.logger.info("try %s time" % i)
            self.device.delay(1)
            if self.is_no_files_in_gallery():
                self.logger.info("no media files")
                break
            elif media_item.exists:
                count = media_item.count
                self.logger.info("found %s pic" % count)
                media_item.click.wait()
                for i in range(count):
                    self.logger.info("try to del %s file" % (i+1))
                    self.del_file_without_check()
            else:
                self.back_to_gallery_home()
            self.device.delay(5)
        self.logger.info("del all media files done")

    def is_no_files_in_gallery(self):
        no_photos = self.device(text="No photos")
        return no_photos.wait.exists()

    def back_to_gallery_home(self):
        for i in range(5):
            if not self.top_tab.wait.exists():
                self.device.press.back()

    def del_trash(self):
        self.enter()

        self.device(descriptionMatches="Albums|albums").click()
        self.device.wait.idle()

        content = self.device(resourceId="com.tclhz.gallery:id/fragment_album_recyclerview")
        x, y = self.generate_trash_loaction()
        self.device.click(x, y)

        self.device(description="Empty").click()
        self.device.wait.idle()

        self.device(text="EMPTY").click()
        self.device.wait.idle()

        # self.device.delay(1)
        # self.device(description='Select all').click()
        # self.device.wait.idle()
        # self.device.delay(1)
        # self.device(resourceId="com.tclhz.gallery:id/trash_items_delete").click()
        # # self.device.wait.idle()
        # self.device.delay(2)
        # # self.device(text="DELETE").click()
        # self.click_text_DELETE()
        # verify
        if self.device(text="Trash").wait.gone(timeout=60*1000):
            self.logger.info("trash del success")
            return True
        self.logger.error("******* trash del within 60s ******")
        return False

    def generate_trash_loaction(self):
        x, y = self.device(text="Trash").get_location()
        self.logger.info("Text Trash loc x={}, y={}".format(x, y))

        return x, y-200



if __name__ == '__main__':
    g = Gallery('62e36630', 'Gallery')
    # g.del_trash()
    g.del_file()
    # g.open_file(index=1)
    # print g.gen_loc_for_swipe(orientation='h', rate_from=0.8, rate_to=0.2)
    # time.sleep(1)
    # sx, sy, ex, ey = g.gen_loc_for_swipe(orientation='h', rate_from=0.8, rate_to=0.2)
    # print(sx, sy, ex, ey)
    # for i in range(10):
    #     g.swipe_file(sx, sy, ex, ey, steps=10)

    # for i in range(10):
    #     g.del_file()
