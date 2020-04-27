# coding=utf-8
"""Browser library for scripts.
"""
from common import *


class Browser(Common):

    baidu = 'www.baidu.com'
    def __init__(self, device, log_name):
        Common.__init__(self, device, log_name)
        self.appconfig.set_section("Browser")
        self.company = "hawk" if self.isMILAN_GL else "hawk"
        self.menu_bar_btn = self.device(
            resourceId="com.%s.android.browser:id/menu_toolbar" % (self.company))
        self.browser_package = self.device(resourceId="com.%s.android.browser" % (self.company))
        self.browser_exit = self.device(resourceId="com.%s.android.browser:id/ck_ask" % (self.company))
        self.exit_confim = self.device(
            resourceId="com.%s.android.browser:id/tv_confirm" % (self.company))
        self.index_download_completed = self.device(textStartsWith="Download complete")
        self.package = "com.tcl.android.browser"

    def enter(self):
        """Launch browser.
        """
        if self.menu_bar_btn.wait.exists(timeout=1000):
            return True
        self.logger.debug('enter browser')
        self.start_app("Browser")
        self.device.delay(2)
        if self.menu_bar_btn.wait.exists(timeout=1000):
            self.logger.debug("enter browser success")
            return True
        return False

    def setup(self):
        self.clear(self.package)
        self.enter()
        time.sleep(3)
        # self.start_app("Browser")
        if self.device(text="ALLOW").exists:
            self.device(text="ALLOW").click()
        if self.device (text="ALLOW ONLY WHILE USING THE APP").exists:
            self.device(text="ALLOW ONLY WHILE USING THE APP").click()
        if self.device(text="ALLOW").exists:
            self.device(text="ALLOW").click()
        time.sleep(1)
        if self.device(text="Allow Cookies").exists:
            self.device (text="Allow Cookies").click()
        cn_web_sites = ["www.baidu.com", "http://m.hao123.com", "http://image.baidu.com/", "https://dushu.baidu.com/",
                        "https://news.baidu.com"]
        us_web_sites = ["www.google.com", "www.facebook.com", "www.python.org", "www.yahoo.com", "www.youtube.com"]

        web_sites = us_web_sites if self.config.site == "US" else cn_web_sites

        for url in web_sites:
            self.pre_add_bookmarks(url)

        # self.del_bookmark("https://3g.my-onetouch.com/")
        self.exit_and_confim()

    def exit_and_confim(self):
        self.home()
        self.menu_bar_btn.click()
        self.device(text="Quit").click()
        self.device(text="Clear history & cache").click()
        self.device(text="Don't ask again").click()
        self.device(text="CONFIRM").click()

    def pre_add_bookmarks(self,website):
        try:
            self.browser_webpage(website)
            if "www.baidu.com" == website and self.device(text="SHARE LOCATION").exists:
                self.device(text="SHARE LOCATION").click()
            self.save_bookmark(website)
        except:
            self.logger.warning(traceback.format_exc())

    def exit(self):
        """exit browser.
        """
        self.logger.debug('exit browser')
        for i in range(50):
            if self.browser_package.exists:
                self.device.press.back()
                if self.browser_exit.exists:
                    self.browser_exit.click()
                    self.device.wait.idle()
                if self.exit_confim.exists:
                    self.exit_confim.click()
                self.device.delay(1)
            else:
                break
        else:   # browser do not exist after back 50 times, clear all, and restart browser
            self.logger.error("******* can not exist browser, clear all  ******")
            self.clear_background()
            self.enter()
        return True

    def home(self):
        '''back to homepage
        '''
        homeid = self.device(
                             resourceId="com.%s.android.browser:id/url" % self.company)
        self.logger.info("back to homepage")
        for i in range(5):
            self.device.delay(3)
            if homeid.wait.exists(timeout=2000):
                return True
            self.device.press.back()
        else:
            self.back_to_home()
            self.logger.error("******* can not exist browser, clear all  ******")
            self.clear_background()     # add clear background, some times can not back to browser home
            self.enter()

        # verify
        if homeid.wait.exists(timeout=2000):
            return True

        return False

    def browser_webpage(self, website=None):
        """browser webpage
        """
        addr = self.appconfig('web_page_download', "Chrome") if website is None else website
        self.logger.info("browser webpage %s" % addr)
        assert self.home(), 'Can ont go to home activity'
        self.device(resourceId="com.hawk.android.browser:id/url").click()
        self.device.delay(1)
        self.adb.input(addr)
        self.device.delay(1)
        self.device.press.enter()
        self.device.delay(10)
        self.logger.debug('loading...')

        # verify
        if not self.device(resourceId="com.%s.android.browser:id/stop" % self.company).wait.gone(timeout=120 * 100):
            self.logger.debug("%s open fail!" % website)
            self.save_fail_img()
            return False
        else:
            self.logger.debug("%s load success!" % website)
            self.device.delay(2)
            return True

    def save_bookmark(self, page=None):
        '''save current page to bookmark
        '''

        page = self.appconfig('web_page_download', "Chrome") if page is None else page
        self.logger.debug("save %s to bookmark" % page)

        self.open_menu()
        self.go_to_menu_item('Add Bookmark')
        self.device.wait.idle()

        # verify
        if self.is_in_menu():
            self.logger.error("set %s to bookmark failed" % page)
            self.save_fail_img()
            return False
        else:
            self.logger.debug("set %s to bookmark success" % page)
            return True

    def del_bookmark(self, page=None):
        '''delete bookmark -- page
        '''
        page = self.appconfig('web_page_download', "Chrome") if page is None else page
        self.logger.debug("delete %s bookmark" % page)
        self.open_menu()
        self.go_to_bookmark_history()
        self.go_history_tab('bookmark')
        count = self.device(resourceId="com.%s.android.browser:id/parent" % self.company).count
        # for i in range(count):
        #     if self.device(resourceId="com.%s.android.browser:id/parent" % self.company, index=i).child(
        #             textContains=page).wait.exists(timeout=1000):
        #         self.logger.info("fond bookmark")
        #         self.device(resourceId="com.%s.android.browser:id/parent" % self.company, index=i).child(
        #             resourceId="com.%s.android.browser:id/bookmark_item_more" % self.company).click()
        #         self.device.wait.idle()
        #         break
        if self.device(text=page).right(resourceId="com.hawk.android.browser:id/bookmark_item_more").exists:
            self.logger.info("found bookmark {} by method:d(A).right(B) ******".format(page))
            self.device (text=page).right (resourceId="com.hawk.android.browser:id/bookmark_item_more").click()
        else:
            self.logger.error("******* can not find bookmark {} ******".format(page))
            return False
        self.device(text="Clear").click()
        self.device.wait.idle()

        self.device(text='CLEAR').click()
        self.device.wait.idle()

        if not self.device(textContains=page).exists:
            self.logger.debug("delete %s bookmark success" % page)
            return True
        else:
            self.logger.error("delete %s bookmark failed" % page)
            self.save_fail_img()
            return False

    def clear_data(self):
        """clear data of browser
        """
        self.logger.debug('Clear browser data')

        # go Home
        self.home()

        # assert menu bar
        self.open_menu()

        # open history
        self.go_to_bookmark_history()
        self.go_history_tab('history')

        if self.is_no_histroy():
            self.logger.info("history cleared")
            return True
        time.sleep(1)
        # clear all
        if self.device(text="CLEAR ALL").exists:
            self.device(text="CLEAR ALL").click()
        self.device.wait.idle()
        if self.device (text="CLEAR").exists:
            self.device(text="CLEAR").click()
        self.device.wait.idle()

        # verify
        if self.is_no_histroy():
            self.logger.info("history cleared")
            return True
        else:
            self.logger.error("******* can not clear history ******")
            return False

    def is_no_histroy(self):
        if self.device(text="No browsing history").wait.exists(timeout=3000):
            self.logger.info("history cleared")
            return True
        return False

    def open_menu(self):
        assert self.menu_bar_btn.wait.exists(), "**** can not find menu bar ****"
        self.menu_bar_btn.click.wait(timeout=3000)

    def go_to_menu_item(self, item):
        assert self.is_in_menu(), "can not find menu"
        self.device(text=item).click()
        self.device.wait.idle()

    def go_to_bookmark_history(self):
        self.go_to_menu_item('Bookmarks/History')

    def go_history_tab(self, tab):
        tabs = {'bookmark': 1, 'history': 0, 'saved': 2}
        self.device(className="android.widget.ImageButton", index=tabs.get(tab)).click()
        self.device.wait.idle()
    
    def is_in_menu(self):
        if self.device(resourceId="com.%s.android.browser:id/pager_common_menu_id" % self.company).wait.exists(
                timeout=1000):
            return True
        else:
            return False

    def select_bookmark(self, number):
        """load webpage from bookmark
        """
        self.logger.info("open bookmarks %d" % (number + 1))

        # assert menu bar
        self.open_menu()

        # open history
        self.go_to_bookmark_history()
        self.go_history_tab('bookmark')

        self.device(resourceId="com.%s.android.browser:id/parent" % self.company, index=number).click()
        self.device.wait.idle()

        self.logger.debug('loading...')
        self.device.delay(2)
        if not self.device(resourceId="com.%s.android.browser:id/stop" % self.company).wait.gone(timeout=30000):
            self.logger.debug("Bookmark %s load failed!" % (number + 1))
            self.save_fail_img()
            return False
        self.logger.debug("Bookmark %s load success!" % (number + 1))
        return True

    def navigation(self):
        bef_url = self.device(resourceId="com.%s.android.browser:id/url" % self.company).get_text()
        self.logger.debug("Before URL: %s" % bef_url)

        # click some link to change url
        # self.device.click(120, 571)
        self.logger.debug("click more channel")
        self.device(text="更多频道").click()
        # self.device.click(944, 733)#click  more
        self.device.delay(2)

        if self.device(resourceId="com.%s.android.browser:id/stop" % self.company).wait.gone(timeout=60000):
            self.device.delay(2)
            af_url = self.device(resourceId="com.%s.android.browser:id/url" % self.company).get_text()
            self.logger.debug("After URL: %s" % af_url)
            if bef_url != af_url:
                self.logger.info("Navigation %s success." % af_url)
                self.device.delay(2)
                self.device.press.back()
                if self.device(resourceId="com.%s.android.browser:id/stop" % self.company).wait.gone(timeout=60000):
                    if self.device(resourceId="com.%s.android.browser:id/url" % self.company).get_text() == bef_url:
                        self.logger.info("back %s success" % bef_url)
                        self.device.delay(2)
                        return True
        self.logger.info("Navigation %s failed." % bef_url)
        self.save_fail_img()
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
        download = self.device(textMatches="Download|DOWNLOAD")
        if download.wait.exists():
            download.click.wait(timeout=3000)
        allow = self.device(textMatches="ALLOW DOWNLOAD|REPLACE FILE")
        for i in range(2):
            if allow.wait.exists():
                allow.click()
                self.device.wait.idle()

        # verify
        self.device.open.notification()
        if self.index_download_completed.wait.exists(timeout=60000):
            self.logger.info("download %s success" % filetype)
            self.device.press.back()
            return True

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

    def is_playing_streaming(self, filetype='RTSP', loop=0):
        """whether playing streaming
        """
        self.logger.info("click streaming start")
        self.browser_webpage(self.appconfig('web_page_download', "Chrome"))  # http://60.12.220.48:8080/stability.jsp
        self.device(text=filetype).click.wait(timeout=2000)
        if loop == 0 and self.device(text="Open with").wait.exists(timeout=2000):
            self.device(text="Gallery").click()
            self.device.delay(1)
            self.device(text="ALWAYS").click()
        self.device.delay(15)
        if self.is_playing_video() or self.device(description="a.3gp").wait.gone(timeout=1000):
            return True
        else:
            self.save_fail_img()
            return False

if __name__ == '__main__':
    a = Browser("GAWKFQT8WGL7L7S8", "Browser")
    a.save_bookmark("http://60.12.220.48:8080/stability.jsp")
    a.del_bookmark("http://60.12.220.48:8080/stability.jsp")