#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os
import random
import sys
import traceback
import unittest

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not lib_path in sys.path:
    sys.path.append(lib_path)
from common.settings import Settings
from common.settings import Wifi
from common.mods import Mods
from common.base_test_case import BaseTestCase
from common.browser import Browser
from common.chrome import Chrome
from TclTools import upload_device_info
from TclTools import time_utils

class TestBrowser(BaseTestCase):
    test_mod = Mods.Browser

    @classmethod
    def setUpClass(cls):
        """必须关闭wifi"""
        super(TestBrowser, cls).setUpClass()
        cls.mod = Browser(cls.c.device, cls.test_mod)
        cls.set = Settings(cls.c.device, "Settings")
        cls.wifi = Wifi(cls.c.device, "task_Wifi")
        cls.chrome = Chrome(cls.c.device, 'Chrome')
        cls.mod.device.watcher("ALLOW_BAIDU_LOC") \
            .when(textContains="use your device's location") \
            .when(text="ALLOW") \
            .click(text="ALLOW")
        cls.mod.device.watcher("SHARE_LOACATION") \
            .when(textContains="SHARE LOCATION") \
            .click(textContains="SHARE LOCATION")
        cls.mod.disable_wifi()

    # @unittest.skip("for debug")
    def testStability3G(self):
        """
        remove download cases sync from Krypton
        :return:
        """
        if self.mod.config.testtype == "MINI":
            return
        if self.set.get_carrier_service_num() == "10086":
            self.set.logger.info("you are using CMCC sim card, using 4G instead of 3G test cases")
            self.set.switch_network_for_multi_menus("ALL")
        else:
            self.set.switch_network_for_multi_menus("3G")

        # basic test cases
        self.case_open_webpage(int(self.dicttesttimes.get("Page3G".lower(), 0)))
        self.case_open_bookmark(int(self.dicttesttimes.get("Bookmark3G".lower(), 0)))
        self.case_webnavigation(int(self.dicttesttimes.get("Navigation3G".lower(), 0)))

        # downloading related
        self.case_download("Text", int(self.dicttesttimes.get("DownloadText3G".lower(), 0)))
        self.case_download_play("Music", int(self.dicttesttimes.get("DownloadAudio3G".lower(), 0)))
        self.case_download("Picture", int(self.dicttesttimes.get("DownloadPicture3G".lower(), 0)))
        self.case_download_play("Video", int(self.dicttesttimes.get("DownloadVideo3G".lower(), 0)))
        self.case_play_streaming('RTSP', int(self.dicttesttimes.get("Streaming3G".lower(), 0)))

    # @unittest.skip("for debug")
    def testStabilityLTE(self):
        """
        remove download cases sync from Krypton
        :return:
        """
        # self.set.switch_network_for_multi_menus("ALL")  # add try catch in this method

        # basic test cases
        self.case_open_webpage(int(self.dicttesttimes.get("PageLTE".lower(), 0)))
        self.case_open_bookmark(int(self.dicttesttimes.get("BookmarkLTE".lower(), 0)))
        self.case_webnavigation(int(self.dicttesttimes.get("NavigationLTE".lower(), 0)))

        # downloading related
        self.case_download("Text", int(self.dicttesttimes.get("DownloadTextLTE".lower(), 0)))
        self.case_download_play("Music", int(self.dicttesttimes.get("DownloadAudioLTE".lower(), 0)))
        self.case_download("Picture", int(self.dicttesttimes.get("DownloadPictureLTE".lower(), 0)))
        self.case_download_play("Video", int(self.dicttesttimes.get("DownloadVideoLTE".lower(), 0)))
        self.case_play_streaming('RTSP', int(self.dicttesttimes.get("StreamingLTE".lower(), 0)))

    # @unittest.skip("for debug")
    def testJank(self):
        """
        just test in China
        :return:
        """

        if self.mod.config.site == "US":
            return
        self.chrome._copy_test_web_files()
        # 获取数据
        data = self.case_jankiness_main(self.mod.adb.device_serial())

        # 处理数据
        v = self.parser_jankiness(data)
        jank_count = {
            'serial': self.mod.adb.device_serial(),
            'value': v,
            'timestamp': time_utils.timestamp_in_ns()
        }

        # 上传数据
        upload_device_info.send_jank(jank_count, self.logger)

    def parser_jankiness(self, data):
        """
        {'ChromeWebPagePanUp': [
                                    {'frameRate': 0, 'jankinessCount': 0, 'maxDeltaVsync': 0},
                                    {'frameRate': 0, 'jankinessCount': 0, 'maxDeltaVsync': 0}
                               ],
        'ChromeWebPagePanDown': [
                                    {'frameRate': 0, 'jankinessCount': 0, 'maxDeltaVsync': 0},
                                    {'frameRate': 23.939164645722386, 'jankinessCount': 0, 'maxDeltaVsync': 4.0}
                                ],
        }

        解析测试结果，生成几次jank数量的和
        :param data:
        :return:
        """
        ret = 0
        try:
            for k, d in data.items():
                for item in d:
                    jankinessCount = item['jankinessCount']
                    ret += jankinessCount
                    self.logger.info("{} - {}".format(k, d))
            self.logger.info("jankinessCount: {}".format(ret))
            return ret
        except:
            self.logger.info(traceback.format_exc())
            return -1

    def case_jankiness_main(self, device_id):
        # init valuse
        trace_time = 5
        package = 'com.android.chrome'
        activity = 'com.google.android.apps.chrome.Main'

        # start chrome by activity name
        # self.mod.adb.startactivity(package, activity)
        # self.mod.device.delay(5)

        # go to url, the file saved in local
        # url = 'file://////sdcard/testdata/Home-ESPN.html'
        # self.chrome.go_to_url(url)
        self.chrome.open_html_form_storage()
        self.mod.device.wait.idle()

        # perform jankiness test
        data_list = {}
        for _ in range(trace_time):
            case_name, data = self.chrome.test_web_view_scrolling(device_id)
            data_list[case_name] = data
            # jdh.add_test_datas(case_name, data)
            case_name, data = self.chrome.test_web_view_flinging(device_id)
            # jdh.add_test_datas(case_name, data)
            data_list[case_name] = data
            case_name, data = self.chrome.test_web_view_zoom_in(device_id)
            # jdh.add_test_datas(case_name, data)
            data_list[case_name] = data
            self.mod.device.swipe(200, 400, 200, 200)
            case_name, data = self.chrome.test_web_view_zoom_out(device_id)
            data_list[case_name] = data
            # jdh.add_test_datas(case_name, data)
            case_name, data = self.chrome.test_web_view_pan_left(device_id)
            data_list[case_name] = data
            # jdh.add_test_datas(case_name, data)
            case_name, data = self.chrome.test_web_view_pan_right(device_id)
            # jdh.add_test_datas(case_name, data)
            data_list[case_name] = data
            case_name, data = self.chrome.test_web_view_pan_down(device_id)
            # jdh.add_test_datas(case_name, data)
            data_list[case_name] = data
            case_name, data = self.chrome.test_web_view_pan_up(device_id)
            # jdh.add_test_datas(case_name, data)
            data_list[case_name] = data
            self.chrome.swipe_main_view_to_beginning()

        return data_list

    def case_open_webpage(self, times=1):
        self.mod.logger.debug("Open a webpage %d times." % times)
        self.mod.enter()
        for index in range(times):
            try:
                self.mod.clear_data()
                self.mod.home()
                if self.mod.browser_webpage() and self.mod.save_bookmark() and self.mod.del_bookmark():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.home()
        self.mod.exit()
        self.mod.logger.debug("Open a webpage %d times complete." % times)

    def case_open_bookmark(self, times=1):
        self.mod.logger.debug("Open bookmarks %d times." % times)
        self.mod.enter()
        # self.mod.clear_data()
        for index in range(times):
            try:
                if self.mod.select_bookmark(random.randint(1, 4)):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.enter()
            finally:
                self.mod.home()
        self.mod.exit()
        self.mod.logger.debug("Open bookmarks %d times complete." % times)

    def case_download(self, filetype, times=1):
        '''download text / picture
        '''
        self.mod.logger.debug('Download %s %d Times' % (filetype, times))
        self.mod.enter()
        self.mod.home()
        # self.mod.clear_data()
        for loop in range(times):
            try:
                if self.mod.download_from_jsp(filetype):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.enter()
            finally:
                self.mod.clear_notification()
                self.mod.home()
        self.mod.exit()
        self.mod.logger.info("download %s Test complete" % filetype)

    def case_download_play(self, filetype, times=1):
        self.mod.logger.debug('Download and play %s %d Times' % (filetype, times))
        self.mod.enter()
        self.mod.home()
        for loop in range(times):
            try:
                # if self.mod.download_from_jsp(filetype) and self.mod.play_file(filetype, loop):
                if self.mod.download_from_jsp(filetype):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
                self.mod.enter()
            finally:
                self.mod.home()
        self.mod.exit()
        self.mod.logger.info("Download and play %s Test Completed" % filetype)

    def case_webnavigation(self, times=1):
        self.mod.logger.debug('web Navigation %d Times.' % (times))
        self.mod.enter()
        self.mod.home()
        # webpage_url = 'm.sogou.com'
        webpage_url = 'www.qq.com'
        for index in range(times):
            try:
                if self.mod.browser_webpage(webpage_url) and \
                        self.mod.navigation():
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.home()
        self.mod.exit()
        self.mod.logger.debug('web Navigation %d Times complete.' % times)

    def case_play_streaming(self, filetype, times=1):
        self.mod.logger.debug("Play Streaming  %d times" % times)
        self.mod.enter()
        self.mod.home()
        # self.mod.clear_data()
        # self.mod.browser_webpage(self.mod.appconfig("Streaming", "Chrome"))
        for loop in range(times):
            try:
                if self.mod.is_playing_streaming():
                        # and self.mod.back_to_webpage(self.mod.appconfig("Streaming", "Chrome").split(r"//")[1]):
                    self.trace_success()
                else:
                    self.trace_fail()
            except:
                self.mod.logger.warning(traceback.format_exc())
                self.mod.save_fail_img()
            finally:
                self.mod.home()
        self.mod.exit()
        self.mod.logger.debug("Play Streaming %d times complete" % times)


if __name__ == '__main__':
    suiteCase = unittest.TestLoader().loadTestsFromTestCase(TestBrowser)
    suite = unittest.TestSuite([suiteCase])
    unittest.TextTestRunner(verbosity=2).run(suite)
