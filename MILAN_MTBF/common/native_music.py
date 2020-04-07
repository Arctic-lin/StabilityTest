"""Camera library for scripts.
"""

from common import *

#3/15 11:09,new mtbf script for local music apk ,base on google_music.py
class native_Music(Common):
    package = 'com.tct.music'

    def setup(self):
        self.logger.info('reboot device for triggering media file scan on device')
        self.adb.cmd('reboot')
        time.sleep(60)
        self.logger.info('device boot')
        self.device.wakeup()
        if self.device(resourceId="com.android.systemui:id/battery_rect").wait.exists(timeout=3000):
            sx, sy, ex, ey = 225, 2032, 225, 648
            self.device.swipe(sx, sy, ex, ey, steps=10)
        self.clear(self.package)
        self.enter()
        time.sleep(10)
        self.allow_permissions()
        if self.device(textMatches="Shuffle all.*").wait.exists(timeout=3000):
            self.device(textMatches="Shuffle all.*").click()
        self.device.delay()
        if self.device(resourceId="%s:id/iv_play"%self.package).wait.exists(timeout=3000):
            self.device(resourceId="%s:id/iv_play"%self.package).click()
            self.device.delay(1)

        # el = self.device(text='The 2nd Law')
        # el.click.wait()
        # el = self.device(resourceId='com.google.android.music:id/fab_play')
        # el.click.wait()
        # time.sleep(5)
        # el = self.device(resourceId='com.google.android.music:id/play_pause_header')
        # el.click.wait()
        self.device.press.back()
        self.device.press.home()

    def enter(self):
        """Launch music by StartActivity.
        """
        self.logger.debug('enter music')
        # if self.device(packageName="com.google.android.music").wait.exists(timeout=5000) and \
        #         self.device(resourceId="com.google.android.music:id/progress_spinner").wait.gone(timeout=10000):
        #     return True
        self.start_app("Music",b_desk=False)
        # if self.device(text="SKIP").wait.exists():
        #     self.device(text="SKIP").click.wait()
        # return self.device(packageName="com.google.android.music").wait.exists(timeout=5000) and \
        #        self.device(resourceId="com.google.android.music:id/progress_spinner").wait.gone(timeout=10000)

    def play_music(self):
        self.logger.debug(" Start music player.")
        # if self.device(resourceId="com.google.android.music:id/play_drawer_list").exists:
        #     self.device.press.back()
        #
        # if not self._is_liston_now_activity():
        #     self.logger.debug("is not liston now activity")
        #     # self.enter()
        #     try:
        #         self.go_to_menu_item("Listen Now")
        #     except:
        #         self.go_to_menu_item("Listen now")
        # else:
        #     self.logger.debug("is liston now activity")
        self.enter()
        self.goto_song()
        if self.device(textMatches="Shuffle all.*").exists:
            self.device(textMatches="Shuffle all.*").click()
            self.device(textMatches="Shuffle all.*").click()  # double confirm shuffle all clicked
            self.device.delay(2)
        music = self.device(resourceId="%s:id/songs_title"%self.package).get_text()
        self.logger.info("start play music %s" % music)
        self.device.delay(2)
        if self.is_playing_music():
            self.device.delay(5)
            self.logger.info("play music %s success" % music)
            return True
        self.logger.info("play music %s failed" % music)
        self.save_fail_img()
        return False
    def goto_song(self):
        if self.device(text="SCAN SETTINGS").exists:
            self.logger.debug(" Music in settings interface,back to music home.")
            self.device (resourceId="%s:id/img_left"%self.package).click ()
            time.sleep(1)
            if self.device(text="Songs").exists:
                self.device (text="Songs").click()
        elif self.device(resourceId="%s:id/iv_back"%self.package).exists:
            self.device (resourceId="%s:id/iv_back"%self.package).click ()
            if self.device(text="Songs").exists:
                self.device (text="Songs").click()


    def close_music(self):
        self.back_to_home()
        self.logger.info("closed music")
        if self.is_playing_music():
            self.device.open.notification()
            # self.device(description="Pause").click.wait(timeout=2000)
            if self.device(resourceId="%s:id/iv_stop"%self.package).exists:
                self.device (resourceId="%s:id/iv_stop"%self.package).click()
            # if self.device(resourceId="com.android.systemui:id/dismiss_text").wait.exists():
            #     self.device(resourceId="com.android.systemui:id/dismiss_text").click()
            # else:
            #     self.device.press.home()
            if not self.device(resourceId="%s:id/ly_notification_quick_control"%self.package).exists:
                self.logger.info("closed music success")
                return True
            self.logger.info("closed music failed")
            return False
        else:
            self.logger.info("music is not playing")
            return True

    def go_to_menu_item(self, param):
        """
        go to item in menu
        :param param:
        :return:
        """
        self.open_menu()
        music_library = self.device(text=param)
        assert music_library.wait.exists(), "******** can not find option: %s********" % param
        music_library.click.wait(timeout=3000)

    def open_menu(self):
        """
        open music menu
        :return:
        """
        if self.device(resourceId="com.google.android.music:id/play_drawer_list").wait.exists():
            return True
        assert self.is_music_home(), "***** can not open music menu *****"
        self.device(description="Show navigation drawer").click.wait()

        assert self.device(
            resourceId="com.google.android.music:id/play_drawer_list").wait.exists(), "******** can not find menu detailed ********"

    def _is_liston_now_activity(self):
        listen_now = self.device(text="Listen Now").wait.exists(timeout=3000)
        return self.is_music_home and listen_now

    def _is_music_library_activity(self):
        music_library = self.device(text="Music library").wait.exists(timeout=3000)
        return self.is_music_home and music_library

    def is_music_home(self):
        """
        if menu and search btn exist, it is music home
        :return:
        """
        menu = self.device(description="Show navigation drawer").wait.exists(timeout=2000)
        search = self.device(resourceId="com.google.android.music:id/search").wait.exists(timeout=2000)
        return menu and search

    def click_tab(self, param):
        """
        click tap in Music library activity
        :param param: 
        :return: 
        """
        assert self._is_music_library_activity(), "do not in music library activity"

        tab = self.device(text=param)
        assert tab.wait.exists(), "******** can not find tab: %s  ********" % param
        tab.click.wait(timeout=3000)

    def shuffle_all(self):
        """
        steps for clicking SHUFFLE ALL
        :return: 
        """
        if not self._is_music_library_activity():
            self.go_to_menu_item("Music library")

        assert self._is_music_library_activity(), "***** can not go to music library *****"
        self.click_tab("SONGS")

        shuffle_all = self.device(text="SHUFFLE ALL")
        assert shuffle_all.wait.exists(), "******** can not find SHUFFLE ALL  ********"
        shuffle_all.click.wait(timeout=3000)

    def observe_navigation(self):
        """
        observe navigation, such as play, pause, next, previous btn
        :return:
        """
        self.logger.info("observe navigation")
        if self.device(resourceId="com.google.android.music:id/header_pager").wait.exists(timeout=3000):
            self.device(resourceId="com.google.android.music:id/header_pager").click.wait()

        # make sure song details activity is opened
        assert self.device(resourceId="com.google.android.music:id/thumbsup").wait.exists(), \
            "******** can not find thumbsup, means can not open song details activity  ********"

        display_play = self.device(description="Play").wait.exists(timeout=3000)  # music should NOT be playing
        display_pause = self.device(description="Pause").wait.exists(timeout=3000)  # music should be playing

        # observe navigation play/pause
        self.logger.info("observe play pause")
        if display_play:
            assert not self.is_playing_music2(), "music should not be playing when %s" % display_play
            display_play.click()

        assert self.is_playing_music2(), "music should be playing"
        assert display_pause, "shuld display %s when music is playing" % display_pause

        # observe next, previous
        self._observe_next_previous("Next")
        self.device.delay(2)
        # self._observe_next_previous("Next")
        # can not add any delay here! back to previous song when played within 2s
        self._observe_next_previous("Previous")

    def _observe_next_previous(self, next_or_previous):
        self.logger.info("oberve action: %s" % next_or_previous)
        previous_playing = self.device(resourceId="com.google.android.music:id/trackname").get_text()

        action_btn = self.device(description=next_or_previous)
        assert action_btn.wait.exists(), "******** can not find btn:%s ********" % next_or_previous
        if next_or_previous == "Previous":
            action_btn_coo = action_btn.info["bounds"]
            action_btn_y = (action_btn_coo["top"] + action_btn_coo["bottom"]) / 2
            action_btn_x = (action_btn_coo["right"] + action_btn_coo["left"]) / 2
            # print action_btn_x, action_btn_y
            self.device.click(action_btn_x, action_btn_y)
            self.device.click(action_btn_x, action_btn_y)
            self.device.wait("idle")
        else:
            action_btn.click.wait(timeout=3000)

        self.device.delay(1)
        current_playing = self.device(resourceId="com.google.android.music:id/trackname").get_text()

        assert not previous_playing == current_playing, "previous song(%s) should not equal current song(%s)" % (
            previous_playing, current_playing)


if __name__ == '__main__':
    a = Music("GAWKFQT8WGL7L7S8", "Music")
    # print a.device.dump(r"c:\recorder.xml")
    a.setup()
