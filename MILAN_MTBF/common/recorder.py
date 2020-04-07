#!coding=utf-8
"""Recorder library for scripts.
"""

import traceback

from common import Common


class Recorder(Common):
    """Provide common functions involved Sound Recorder."""

    def __init__(self, device, log_name):
        super(Recorder, self).__init__(device, log_name)
        self.record_btn = self.device(
            resourceId='com.%s.soundrecorder:id/recordButton' % ("tct" if self.isMILAN_GL else "tcl.tct"))
        self.stop_btn = self.device(
            resourceId='com.%s.soundrecorder:id/stopButton' % ("tct" if self.isMILAN_GL else "tcl.tct"))
        self.record_title = self.device(
            resourceId='com.%s.soundrecorder:id/record_file_item' % ("tct" if self.isMILAN_GL else "tcl.tct"))
        self.record_list_btn = self.device(
            resourceId='com.%s.soundrecorder:id/img_file_list' % ("tct" if self.isMILAN_GL else "tcl.tct"))
        self.del_btn = self.device(resourceId='com.%s.soundrecorder:id/delete' % ("tct" if self.isMILAN_GL else "tcl.tct"))
        self.progress_bar = self.device(
            resourceId='com.%s.soundrecorder:id/stateProgressBar' % ("tct" if self.isMILAN_GL else "tcl.tct"))
        self.record_file_more = self.device(resourceId="com.%s.soundrecorder:id/record_file_more"% ("tct" if self.isMILAN_GL else "tcl.tct"))

        self.company = "tct" if self.isMILAN_GL else "tcl.tct"
        self.app_name = 'Sound Recorder'
        self.package = 'com.%s.soundrecorder' % self.company
        self.launch_activity = 'SoundRecorder'

    def setup(self):
        self.clear(self.package)
        self.start_app(self.app_name)
        self.allow_permissions()

    def click_stop_btn(self):
        self.device.click(832, 1818)

    def enter(self):
        """Launch Recorder by StartActivity.
        """
        self.logger.debug('enter Soundrecorder')
        if self.record_btn.wait.exists(timeout=self.timeout):
            return True
        self.start_app(self.app_name)
        return self.record_btn.wait.exists(timeout=self.timeout)

    def back_main_app(self):
        self.logger.debug("Back to main app")
        for i in range(5):
            if self.record_btn.exists:
                return True
            self.device.press.back()
            self.device.delay(1)
        else:
            self.logger.warning("Cannot back to main app")

    def get_storage_num(self):
        dir_path = self.appconfig('storage_tct', 'Recorder')
        amr_num = self.get_file_num(dir_path, '.amr')
        m4a_num = self.get_file_num(dir_path, '.m4a')
        gpp_num = self.get_file_num(dir_path, '.3gpp')
        return amr_num + m4a_num + gpp_num

    def delete_all_audios(self):
        self.logger.debug('clear audio')
        self.record_list_btn.click.wait()
        for i in range(10):
            if not self.record_title.exists:
                self.logger.info("no audio exists")
                break
            self.record_title.long_click()
            self.del_btn.click.wait()
            self.device(text="DELETE").click()
        self.back_main_app()

    def record(self, filename, duration=25):
        """record audio several seconds.
        argv: (int)duration -- recording time
        """
        self.logger.debug("Record audio %s %s seconds." % (filename, duration))
        file_num = self.get_storage_num()
        self.record_btn.click.wait()
        self.device.delay(1)
        if self.device (description="Save record").exists:
            self.device.delay(duration)
            self.logger.debug("Stop recording audio")
            self.device.click(576, 1240)
        self.device.delay(1)
        self.logger.info("stopped recording")
        el = self.device(resourceId='com.%s.soundrecorder:id/edit_text' % self.company)
        if el.exists:
            el.clear_text()
            el.set_text(filename)
            if self.device(text="SAVE").ext5:
                self.device(text="SAVE").click()
            else:
                x, y = 800, 1310
                self.device.click(x, y)

        # verify
        self.device.delay(2)
        if file_num >= self.get_storage_num():
            self.logger.warning("Save audio fail!!!")
            self.save_fail_img()
            return False
        else:
            self.logger.debug("Save audio success!!!")
            return True

    def enter_audio_list(self):
        """Enter audio file list.
        """
        self.logger.debug("Enter Audio List")
        if self.device(resourceId=self.appconfig.id("id_filelist", "Recorder")).wait.exists(timeout=self.timeout):
            self.device(resourceId=self.appconfig.id("id_filelist", "Recorder")).click()
        if not self.device(text=self.appconfig("filelist_title", "Recorder")).wait.exists(timeout=self.timeout):
            self.logger.warning("Cannot Enter file list")
            return False
        return True

    def play(self, name, duration=8):
        """touch audio according to index.
        argv: (int)index -- file order in list
        """
        self.logger.info("play audio %s " % name)
        if self.record_list_btn.exists:
            self.record_list_btn.click.wait()

        # assert record exist
        el = self.device(text=name)
        assert el.wait.exists(timeout=2000), "**** can not find record {}  ****".format(name)

        # assume playing
        el.click()
        self.device.delay(duration)

        # verify playing, should back to record list, if record is playing
        self.device.press.back()
        if el.wait.exists(timeout=10000):
            return True
        else:
            self.logger.info("Cannot play audio %s." % name)
            self.save_fail_img()
            return False

    def delete_all_audio(self, count=30):
        try:
            self.enter()
            if self.record_list_btn.exists:
                self.record_list_btn.click()
            audio_num = self.get_storage_num()
            if audio_num == 0:
                self.logger.debug("no audios exists,do not need delete")
                return True
            self.logger.debug("Starting to delete all audios %s times" % audio_num)
            audio_num = audio_num if audio_num <= count else count
            for loop in range(audio_num):
                self._delete()
                self.device.wait("idle")
                self.logger.debug("delete audio %d times" % (loop + 1))

            audio_num = self.get_storage_num()
            self.logger.debug("delete all audios completed,the current audio_num is %d" % audio_num)
        except:
            self.logger.warning(traceback.format_exc())
        finally:
            self.device.press.back()

    def _delete(self):
        count=self.device(resourceId="com.%s.soundrecorder:id/record_file_name"%self.company).count
        if count != 1:
            if self.device(resourceId="com.%s.soundrecorder:id/record_file_name"%self.company).exists:
                self.device (resourceId="com.%s.soundrecorder:id/record_file_name"%self.company).long_click()
                if self.device(description="More options").exists:
                    self.device (description="More options").click()
                    self.device.delay(2)
                    if self.device (text="Select all").exists:
                        self.device (text="Select all").click ()
                    self.device.delay (2)
                    self.device (description="Delete").click ()
                    self.device.delay (2)
                    self.device (text="DELETE").click ()
                if self.device (text="No recorded files").exists:
                    return True
        else:
            if self.device(resourceId="com.%s.soundrecorder:id/record_file_more"%self.company).exists:
                self.device (resourceId="com.%s.soundrecorder:id/record_file_more"%self.company).click()
                self.device.delay(1)
                self.device (text="Delete").click ()
                self.device.delay (1)
                self.device (text="DELETE").click ()
            if self.device (text="No recorded files").exists:
                return True

            # if self.record_file_more.exists:
        #     self.record_file_more.click()
        #
        # # self._check_more_clicked()  # click more icon failed sometimes, click location again if 'Delete' do not popup
        # if self.device(text="Delete").exists:
        #     self.device(text="Delete").click()
        #
        # # if self.record_title.ext5:
        # #     self.record_title.long_click()
        # #     self.device.wait.idle()
        # #     if self.del_btn.exists:
        # #         self.del_btn.click.wait()#4D20版本这个按钮点了不弹出DELETE按钮框
        #
        # if self.device(text='DELETE').exists:
        #     self.device(text='DELETE').click()
        # else:
        #     self.click_text_DELETE()

    def _check_more_clicked(self):
        if self.Other:
            if self.device(text="Delete").wait.exists(timeout=2000):
                return
            else:
                self.logger.info("more icon click failed")
                x, y = 996, 372
                self.device.click(x, y)
                self.device.delay(1)


    def delete(self, name):
        """delete audio

        argv: (int)index -- file order in list. Default is 0.
        """
        self.logger.debug("Delete Audio %s." % name)
        self.device.delay(2)
        audio_num = self.get_storage_num()
        el = self.device(text=name)
        if el.wait.exists(timeout=40000):  # add more timeout, seems can not find element when playing record
            self._delete()
            # el.long_click()
            # self.del_btn.click.wait()
            # # self.device(text="DELETE").click()
            # self.click_text_DELETE()
            self.device.delay(2)
            if audio_num <= self.get_storage_num():
                self.logger.warning("Delete audio %s failed." % name)
                self.save_fail_img()
                return False
            else:
                self.logger.warning("Delete audio %s success." % name)
                self.back_main_app()
                return True
        else:
            self.logger.info("audio %s not exists" % name)
            self.save_fail_img()
            return False


if __name__ == '__main__':
    a = Recorder("GAWKFQT8WGL7L7S8", "Recorder")
    a.enter()
    a.record("111")
    a.play("111")
    a.delete("111")
    a.clear()
