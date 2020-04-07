# -*- coding: utf-8 -*-

from common import *
from jankiness.surface_flinger_helper import SurfaceFlingerHelper
from ui_parser import UIParser

APP_WINDOW_Name = 'com.android.chrome/org.chromium.chrome.browser.ChromeTabbedActivity#0'
sfh = SurfaceFlingerHelper()

class Chrome(Common):
    app_name = 'Chrome'
    package = 'com.android.chrome'
    launch_activity = 'com.google.android.apps.chrome.Main'

    def __init__(self,  device, mod, sdevice=None):
        Common.__init__(self, device, mod, sdevice=None)
        self.index_download_completed = self.device(textStartsWith="Download complete")

    def setup(self):
        self.clear(self.package)
        self.start_app(self.app_name)
        el = self.device(textMatches='Accept & continue|ACCEPT & CONTINUE')
        if el.wait.exists(timeout=3000):
            el.click.wait()
        el = self.device(textMatches='No Thanks|NO THANKS|No thanks|No, thanks')
        if el.wait.exists(timeout=3000):
            el.click.wait()
        if self.device(text="我知道了").exists:
            self.device (text="我知道了").click()
        time.sleep(1)
        if self.device(textMatches="Search with Sogo|"
                                   "Chrome can use Sogou for search in China. You can change this in Settings.").exists:
            self.device(resourceId="OK").click()
        self.device(resourceId="com.android.chrome:id/tab_switcher_button").click()
        self.device(resourceId="com.android.chrome:id/new_tab_button").click()
        time.sleep(3)
        self.device.press.home()
        self.clear_background()

    def enter(self):
        """Launch Chrome.
        """
        self.logger.debug('enter Chrome')
        if self.device(resourceId=self.appconfig.id("id_url_bar", "Chrome")).wait.exists(timeout=self.timeout):
            return True
        self.start_app("Chrome")
        if self.device(resourceId="com.android.chrome:id/terms_accept").wait.exists(timeout=5000):
            self.device(resourceId="com.android.chrome:id/terms_accept").click()
            # if self.device(resourceId="com.android.chrome:id/positive_button").wait.exists(timeout=5000):
            #     self.device(resourceId="com.android.chrome:id/positive_button").click()
        if self.device(text="NO THANKS").wait.exists(timeout=2000):
            self.device(text="NO THANKS").click()

    def home(self):
        """back to home page
        """
        self.logger.debug('Back Chrome')
        for i in range(5):
            if self.device(resourceId="com.android.chrome:id/tab_switcher_button").wait.exists(timeout=2000):
                # self.device(resourceId="com.android.chrome:id/tab_switcher_button").click()
                # self.device.delay(2)
                # self.device(description="More options").click.wait(timeout=2000)
                # self.device(text="Close all tabs").click.wait(timeout=2000)
                # self.device(resourceId="com.android.chrome:id/new_tab_button").click()
                return
            self.device.press.back()
        else:
            self.logger.warning("Cannot back to Chrome")
            self.enter()

    def exit(self):
        """exit chrome
        """
        self.logger.debug('Exit chrome')
        for i in range(3):
            if self.device(resourceId="com.android.chrome:id/tab_switcher_button").wait.exists(timeout=2000):
                # self.device(resourceId="com.android.chrome:id/tab_switcher_button").click()
                # self.device(description="More options").click.wait(timeout=2000)
                # self.device(text="Close all tabs").click.wait(timeout=2000)
                # self.device(resourceId="com.android.chrome:id/new_tab_button").click.wait(timeout=2000)
                # self.device.press.back()
                return True
            self.device.press.back()
        self.device.press.back()
        self.device.press.home()

    def browser_webpage(self, website="https://www.baidu.com"):
        """browser web page
        arg：website(str) the web page address
        """
        self.logger.info("browser webpage %s" % website)
        self.device.delay(2)
        if self.device(resourceId="com.android.chrome:id/url_bar").exists:
            self.device(resourceId="com.android.chrome:id/url_bar").set_text(website)
        else:
            self.device(resourceId="com.android.chrome:id/search_box_text").click.wait()
            self.device(resourceId="com.android.chrome:id/url_bar").set_text(website)
        self.device.press.enter()
        self.device.delay(2)
        self.logger.debug('loading...')
        if not self.device(resourceId=self.appconfig.id("id_progress", "Chrome")).wait.gone(timeout=60000):
            self.logger.debug("%s open time out!" % website)
            self.save_fail_img()
            return False
        else:
            self.logger.debug("%s load success!" % website)
            self.device.delay(2)
            return True

    def save_bookmark(self, page=u"百度一下"):
        """save current page to bookmark
        arg：page(str) the bookmark name
        """
        self.logger.debug("save %s to bookmark" % page)
        # delete bookmark if exists
        self.device(description=self.appconfig("options", "Chrome")).click()
        if self.device(description="Edit bookmark").wait.exists(timeout=1000):
            self.device(description="Edit bookmark").click()
            self.device(description="Delete bookmarks").click.wait(timeout=2000)
            self.device(description=self.appconfig("options", "Chrome")).click.wait(timeout=2000)
        # bookmark page
        self.device(description="Bookmark this page").click()
        # important! after bookmark page a notice will appear at the bottom of the screen
        # the edit button on the notice has the same content description attribute of the
        # chrome menu. wait 10 seconds here for the notice gone
        self.device.delay(10)
        self.device(description=self.appconfig("options", "Chrome")).click.wait(timeout=2000)
        self.device(text="Bookmarks").click()
        if self.device(text=page).wait.exists(timeout=2000):
            self.logger.debug("set %s to bookmark success" % page)
            return True
        else:
            self.save_fail_img()
            self.logger.error("set %s to bookmark failed" % page)
            return False

    def del_bookmark(self, page=u"百度一下"):
        """delete bookmark
        arg：page(str) the bookmark name
        """
        self.logger.debug("delete %s bookmark" % page)
        step = [
            {"id": {"text": page}, "action": {"type": "long_click"}},
            {"id": {"description": "Delete bookmarks"}},
        ]
        UIParser.run(self, step)
        self.device.delay(2)
        if not self.device(text=page).exists:
            self.logger.debug("delete %s bookmark success" % page)
            return True
        else:
            self.logger.error("delete %s bookmark failed" % page)
            self.save_fail_img()
            return False

    def clear_data(self):
        """clear data of chrome
        """
        self.logger.debug('Clear browser data')
        # open menu
        if self.device(resourceId="com.android.chrome:id/menu_badge").exists:
            self.device(resourceId="com.android.chrome:id/menu_badge").click()
        elif self.device(description=self.appconfig("options", "Chrome")).exists:
            self.device(description=self.appconfig("options", "Chrome")).click()
        self.device.delay(2)

        # open history
        self.device(text="History").click.wait(timeout=2000)
        self.device.delay(2)

        if self.device(text="No history here").exists:
            self.logger.info("clear data success")
            return True

        # CLEAR BROWSING DATA
        if self.device(textMatches="Clear browsing data…|CLEAR BROWSING DATA…").exists:
            self.device(textMatches="Clear browsing data…|CLEAR BROWSING DATA…").click.wait(timeout=4000)

        # set time range to all, only one spinner in this activity
        self.device(resourceId="com.android.chrome:id/spinner").click()
        if self.device(text="All time").wait.exists(timeout=3000):
            self.device(text="All time").click.wait()

        if self.device(textMatches="Clear data|CLEAR DATA").exists:
            self.device(textMatches="Clear data|CLEAR DATA").click.wait(timeout=4000)
        # confirm clear
        if self.device(text="CLEAR").wait.exists(timeout=3000):
            self.device(text="CLEAR").click.wait(timeout=4000)

        # verify waiting for 10s
        if self.device(text="No history here").wait.exists(timeout=10000):
            self.logger.info("clear data success")
            self.home()
            return True
        self.logger.info("clear data failed")
        self.home()

    def select_bookmark(self, number):
        """select an bookmark and open
        arg: number(int) which one bookmark
        """
        self.logger.info("open bookmarks %d" % (number))
        self.device(description=self.appconfig("options", "Chrome")).click.wait(timeout=2000)
        self.device(text="Bookmarks").click.wait(timeout=2000)
        # bookmark = self.device(resourceId="com.android.chrome:id/eb_items_container").child(index=number).child(
        #     index=1).child(index=0).get_text()
        # self.logger.info("the bookmark is %s" % bookmark)
        self.logger.info("open bookmark %d" % (number))
        # self.device(resourceId="com.android.chrome:id/bookmark_items_container").child(index=number).click()
        self.device(resourceId="com.android.chrome:id/recycler_view").child(
            className='android.widget.FrameLayout', index=number).click()
        self.logger.debug('loading...')
        self.device.delay(2)
        if not self.device(resourceId=self.appconfig.id("id_progress", "Chrome")).wait.gone(timeout=30000):
            self.logger.debug("open bookmark %d failed" % (number + 1))
            self.save_fail_img()
            return False
        self.logger.debug("open bookmark %d success" % (number + 1))
        return True

    def is_playing_streaming(self, filetype='RTSP', loop=0):
        """whether playing streaming
        """
        self.logger.info("click streaming start")
        self.browser_webpage(self.appconfig('web_page_download', "Chrome"))  # http://60.12.220.48:8080/stability.jsp
        self.device(text=filetype).click.wait(timeout=2000)
        if loop == 0 and self.device(text="Open with").wait.exists(timeout=2000):
            self.device(text="Video player").click()
            self.device.delay(1)
            self.device(text="ALWAYS").click()
        self.device.delay(15)
        if self.is_playing_video() or self.device(description="a.3gp").wait.gone(timeout=1000):
            return True
        else:
            self.save_fail_img()
            return False

    def back_to_webpage(self, back_url):
        url = self.device(resourceId="com.android.chrome:id/url_bar").get_text()
        self.device.press.back()
        url2 = self.device(resourceId="com.android.chrome:id/url_bar").get_text()
        if url == url2:
            self.device.press.back()
        # if self.device(resourceId=self.appconfig.id("id_progress", "Chrome")).wait.gone(timeout=60000):
        if self.device(className=self.appconfig.id("id_progress", "Chrome")).wait.gone(timeout=60000):
            self.device.delay(2)
            url = self.device(resourceId="com.android.chrome:id/url_bar").get_text()
            self.logger.info("current url %s" % url)
            if back_url in url:
                self.logger.info("back to %s success" % back_url)
                return True
        self.logger.info("back to %s failed" % back_url)
        self.save_fail_img()
        return False

    def navigation(self):
        bef_url = self.device(resourceId="com.android.chrome:id/url_bar").get_text()
        self.logger.debug("Before URL: %s" % bef_url)
        if self.device(text="新闻").exists:
            self.device(text="新闻").click()
        else:
            self.device.click(126, 609)  # the "新闻" location
        self.device.delay(15)  # some time can not detect progressbar, delay 15s here
        af_url = self.device(resourceId="com.android.chrome:id/url_bar").get_text()
        self.logger.debug("After URL: %s" % af_url)
        if bef_url != af_url:
            self.logger.info("Navigation %s success." % af_url)
            return True
        self.logger.info("Navigation %s failed." % bef_url)
        self.save_fail_img()
        return False

    def del_download(self):
        self.logger.debug('Delete all download files')
        self.start_app("Downloads")
        if not self.device(resourceId="com.android.documentsui:id/dir_list").child(index=0).wait.exists():
            self.logger.info("not file exists")
            self.device.press.back()
            return True
        x, y = self.device(resourceId="com.android.documentsui:id/dir_list").child(index=0).get_location()
        self.device.swipe(x, y, x + 1, y + 1, 200)
        self.device(description="More options").click()
        self.device(text="Select all").click()
        self.device(description="delete").click()
        self.device(text="OK").click()
        if not self.device(resourceId="com.android.documentsui:id/dir_list").child(index=0).wait.exists():
            self.logger.info("delete all download files success!!!")
            self.back_to_home()
            return True
        self.logger.debug("delete download failed!!!")
        self.back_to_home()
        return False

    def download(self, filetype):
        '''download file
        '''
        self.logger.info("download %s" % filetype)
        # self.browser_webpage(self.appconfig(filetype, "Chrome"))
        if self.device(text='In progress').wait.gone(timeout=30000):
            # self.device(description=self.appconfig("options", "Chrome")).click.wait(timeout=2000)
            # self.device(text="History").click.wait(timeout=2000)
            if self.device(text="REPLACE FILE").wait.exists():
                self.device(text="REPLACE FILE").click()
            self.device.open.notification()
            if self.device(text="Download complete.").wait.exists(timeout=30000):
                self.logger.info("download %s success" % filetype)
                self.device.press.back()
                return True
        self.logger.info("download %s failed" % filetype)
        self.save_fail_img()
        self.device.press.back()
        return False

    def download_from_jsp(self, filetype):
        """
        for new web page http://60.12.220.48:8080/stability.jsp
        :param filetype:
        :return:
        """
        self.logger.info("download_jsp %s" % filetype)
        self.clear_notification()
        self.device.delay(1)
        self.browser_webpage(self.appconfig('web_page_download', "Chrome"))  # http://60.12.220.48:8080/stability.jsp
        assert self.device(text="New File Download").wait.exists(timeout=5000), "**** It is not stability download test home ****"

        # finish download process
        self.device(text=filetype).click()
        download = self.device(text="DOWNLOAD")
        if download.wait.exists():
            download.click.wait(timeout=3000)
        allow = self.device(text="ALLOW")
        if allow.wait.exists():
            allow.click.wait(timeout=3000)
            if download.wait.exists():
                download.click.wait(timeout=3000)

        # verify
        self.device.open.notification()
        if self.index_download_completed.wait.exists(timeout=30000):
            self.logger.info("download %s success" % filetype)
            self.device.press.back()
            return True

        # if self.device(text='In progress').wait.gone(timeout=30000):  #
        #
        #     if self.device(text="REPLACE FILE").wait.exists():
        #         self.device(text="REPLACE FILE").click()
        #     self.device.open.notification()
        #     if self.device(text="Download complete.").wait.exists(timeout=30000):
        #         self.logger.info("download %s success" % filetype)
        #         self.device.press.back()
        #         return True
        self.logger.info("download %s failed" % filetype)
        self.save_fail_img()
        self.device.press.back()
        return False

    def play_file(self, filetype, loop=0):
        self.logger.info("play %s" % filetype)
        self.device.open.notification()
        self.device.delay(1)
        self.index_download_completed.click()
        self.device.delay()
        if filetype == "Music":
            if loop == 0:
                if self.device(text="Open with").exists:
                    self.device(text="Music").click()
                    self.device(text="ALWAYS").click()
            if (self.device(packageName="com.google.android.music").wait.exists(timeout=2000)) or (
                    not self.index_download_completed.exists):
                self.logger.debug("The music is playing now")
                # self.device.press.back()
                return True
        else:
            if loop == 0:
                if self.device(text="Open with").exists:
                    self.device(text="Photos").click()
                    self.device(text="ALWAYS").click()
            self.device.delay()
            if self.is_playing_video():
                self.device.press.back()
                return True
        self.device.press.back()
        self.logger.info("%s not playing" % filetype)
        self.save_fail_img()
        return False

    def verify_account_login(self, account):
        """
        verify account in Chrome
        :param account:
        :return:
        """
        self.open_menu_item(item="Settings")

        if self.device(text="Sign in to Chrome").wait.exists(timeout=3000):
            self.device(text="Sign in to Chrome").click.wait()
            assert self.device(text=account).wait.exists(timeout=3000), "can not find account %s" % account
        else:
            assert self.device(textContains=account).wait.exists(timeout=3000), "can not find account %s" % account

    def open_menu(self):
        """
        open menu
        :return:
        """
        self.home()
        self.device.wait("idle")
        self.device(description="More options").click()
        self.device(description="More options").wait.gone(timeout=3000)

        assert self.device(description="Refresh page").wait.exists(timeout=3000)

    def open_menu_item(self, item):
        """
        open item in menu
        :param item: 
        :return: 
        """
        self.open_menu()
        item_to_select = self.device(text=item)
        assert item_to_select.wait.exists(), "******** can not find %s  ********" % item
        item_to_select.click.wait(timeout=3000)

    def _copy_test_web_files(self):
        if self.adb.check_web_file_for_jankiness():
            self.logger.info("found web file")
            return
        else:
            self.logger.info("not found web file for jankiness test, copy...")
            source_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'jankiness', 'data')
            self.logger.info(source_path)
            des_path = '/sdcard/testdata'
            ret = self.adb.raw_cmd('-s {} push {} {}'.format(self.adb.device_serial(), source_path, des_path))
            print ret

    def open_html_form_storage(self):
        self.device.press.home()
        self.start_app("File Manager")
        self.device(text = "Internal storage").click()
        self.device(scrollable=True).scroll.vert.to(text="testdata")
        self.device(text="testdata").click()
        if self.device(text="Home-ESPN.html").exists:
            self.device(text="Home-ESPN.html").click()
            # return    # WD, never click chrome
        if self.device(text="Chrome").exists:
            self.device(text="Chrome").click()
        if self.device(text="ALWAYS").exists:
            self.device(text="ALWAYS").click()
        # self.device(text="Home-ESPN.html").click()

    def go_to_url(self, url):
        el = self.device(resourceId='com.android.chrome:id/search_box_text')
        if el.wait.exists(timeout=10):
            el.click()
        el = self.device(resourceId='com.android.chrome:id/url_bar')
        el.set_text(url)
        self.device.press.enter()
        el = self.device(text='ALLOW')
        if el.wait.exists(timeout=2000):
            el.click()

    def swipe_main_view_to_beginning(self):
        max_swipe = 10
        while max_swipe > 0 and self.device.swipe(200, 351, 200, 1479, 60):
            max_swipe -= 1


########################################################################################################################
#                                   Jankiness test cases                                                               #
########################################################################################################################
    def test_web_view_scrolling(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPageScrolling'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        # run at the main window
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            el.scroll.vert.forward()
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
            el.scroll.vert.backward()
        return case_name, test_data

    def test_web_view_flinging(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPageFlinging'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        # run at the main window
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            el.fling.vert.forward()
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
            el.fling.vert.backward()
        return case_name, test_data

    def test_web_view_zoom_in(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPageZoomIn'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        # el.scroll.vert.forward()
        self.device.wait.idle()
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            el.pinch.Out(percent=100, steps=100)
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
            el.pinch.In(percent=150, steps=100)
        return case_name, test_data

    def test_web_view_zoom_out(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPageZoomOut'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        # el.scroll.vert.forward()
        self.device.wait.idle()
        for i in range(NUM_ITERATIONS):
            el.pinch.Out(percent=100, steps=100)
            self.device.wait.idle()
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            el.pinch.In(percent=150, steps=100)
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        return case_name, test_data

    def test_web_view_pan_left(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPagePanLeft'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        # el.scroll.vert.forward()
        self.device.wait.idle()
        el.pinch.Out(percent=200, steps=50)
        self.device.wait.idle()
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            el.swipe.left(steps=50)
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
            el.swipe.right(steps=50)
            self.device.wait.idle()
        el.pinch.In(percent=100, steps=50)
        return case_name, test_data

    def test_web_view_pan_right(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPagePanRight'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        # el.scroll.vert.forward()
        self.device.wait.idle()
        el.pinch.Out(percent=200, steps=50)
        self.device.wait.idle()
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            el.swipe.right(steps=50)
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
            el.swipe.left(steps=50)
            self.device.wait.idle()
        el.pinch.In(percent=100, steps=50)
        return case_name, test_data

    def test_web_view_pan_up(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPagePanUp'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        # el.scroll.vert.forward()
        self.device.wait.idle()
        el.pinch.Out(percent=200, steps=50)
        self.device.wait.idle()
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            el.swipe.up(steps=50)
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
            # el.swipe.down(steps=50)#会把通知栏拉下来
            self.device.swipe(550, 250, 550, 1500, steps=50)
            self.device.wait.idle()
        el.pinch.In(percent=100, steps=50)
        return case_name, test_data

    def test_web_view_pan_down(self, device_id, NUM_ITERATIONS=2):
        case_name = 'ChromeWebPagePanDown'
        print('running case {}'.format(case_name))
        test_data = []
        # chrome = Chrome(device_id)
        el = self.device(resourceId='android:id/content')
        self.device.wait.idle()
        el.pinch.Out(percent=200, steps=50)
        self.device.wait.idle()
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, APP_WINDOW_Name)
            self.device.swipe(200, 351, 200, 1479, 50)
            self.device.wait.idle()
            test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
            self.device.swipe(200, 1479, 200, 351, 50)
            self.device.wait.idle()
        el.pinch.In(percent=100, steps=50)
        return case_name, test_data

if __name__ == '__main__':
    a = Chrome("3dc2a8f3", "Browser")
    a.download_from_jsp('Text')
    # a.enter()
    # a.del_download()
    # a.download("Video")
    # a.play_file("Video")
    # a.clear_notification()
    # a.navigation()
    # a.back_to_webpage()
    # a.home()
    # a.exit()
    # home_url = a.device(resourceId="com.android.chrome:id/url_bar").get_text()
    # a.browser_webpage("wap.sogou.com")
    # a.navigation()
    # a.back_to_webpage(home_url)
    # a.download("Text")
    # a.play_file("Music")
    # a.download_text_picture("Text", 1)
    # a.download_play_audio_vedio("Music", 2)
    # a.download_text_picture("Picture",2)#5
    # a.download_play_audio_vedio("Video", 2)
