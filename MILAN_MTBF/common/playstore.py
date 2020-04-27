from common import *


class PlayStore(Common):
    """Provide common functions involved Play Store."""

    def __init__(self, device, log_name):
        Common.__init__(self, device, log_name)
        self.appconfig.set_section("Store")
        self.open_node=self.device(textMatches="Open|OPEN")
        self.install_node=self.device(textMatches="Install|INSTALL")
        self.uninstall_node=self.device(textMatches="Uninstall|UNINSTALL")
        self.playstore_home = self.device(resourceId="com.android.vending:id/search_bar")

    def enter(self, is_back_main_app=True):
        """enter play store.
        """
        self.logger.debug('enter play store')

        if self.playstore_home.wait.exists(timeout=self.timeout):
            return True
        self.start_app('Play Store')

        # it is slow when open first time
        self.device.delay(5)
        to_check = [self.device(text="ACCEPT"), self.device(text="NO THANKS")]
        for i in range(3):
            self.click_if_exists_in_items(1000, *to_check)
            if self.playstore_home.wait.exists(timeout=self.timeout):
                return True
        else:
            if is_back_main_app:
                self.save_fail_img()
                self.back_main_app()

        if self.playstore_home.wait.exists(timeout=self.timeout):
            return True
        else:
            self.logger.warning('enter play store fail!')
            self.save_fail_img()
            return False

    def exit(self):
        """exit play store.
        """
        self.logger.debug('exit play store')
        for loop in range(4):
            if self.device(packageName='com.tcl.android.launcher').wait.exists(timeout=2000):
                self.device.press.home()
                return True
            self.device.press.back()
        self.logger.debug('exit play store fail!!!')
        self.save_fail_img()
        return False

    def back_main_app(self):
        '''back to play store main screen
        '''
        self.logger.info("back to play store main screen")
        for loop in range(5):
            if self.device(description="Show navigation drawer").wait.exists(timeout=5000):
                return True
            self.device.press.back()
        self.logger.warning("Cannot back to main app")

        if self.enter(False):
            return True
        return False

    def check_interface(self):
        '''check interface in APPS&GAMES / Account&Settings
        '''
        return self.check_apps() and self.check_account() and self.check_setting()

    def check_apps(self):
        self.logger.debug("Check Apps,Games,Movies,Books top free,top paid interface.")
        for application in ["APPS", "GAMES", "MOVIES", "BOOKS"]:
            self.logger.info("Check %s top free& top paid interface." % application)
            if application in ["APPS", "GAMES"]:
                self.device(text="APPS & GAMES").click()
                if application != "APPS":
                    self.device(text=application).click()
                if self.device(text="TOP CHARTS").wait.exists(timeout=5000):
                    self.logger.info("login %s success" % application)
                else:
                    self.logger.info("login %s failed" % application)
                    self.save_fail_img()
                    return False
                self.device(text="TOP CHARTS").click()
                for mark in ["TOP PAID", "TOP GROSSING"]:
                    self.device(text=mark).click()
                    if self.device(resourceId="com.android.vending:id/play_card").wait.exists(timeout=5000):
                        self.logger.info("Check Apps %s success" % mark)
                    else:
                        self.logger.info("Check Apps %s failed" % mark)
                        self.save_fail_img()
                        return False
            else:
                self.device(text="ENTERTAINMENT").click()
                self.device(text=application).click()
                for mark in ["TOP SELLING", "NEW RELEASES"]:
                    self.device(text=mark).click()
                    if self.device(resourceId="com.android.vending:id/play_card").wait.exists(timeout=10000):
                        self.logger.info("Check Apps %s success" % mark)
                    else:
                        self.logger.info("Check Apps %s failed" % mark)
                        self.save_fail_img()
                        return False
                    self.device.press.back()
                self.device.press.back()
            self.back_main_app()
        self.logger.debug("Check Apps,Games,Movies,Books top free,top paid interface success.")
        return True

    def check_account(self):
        self.logger.info("Check interface my account")
        self.back_main_app()
        self.device(description="Show navigation drawer").click.wait()
        if self.device(text="My account").exists:
            self.device(text="My account").click()
            if self.device(text="Add payment method").wait.exists(timeout=5000):
                self.logger.info("Check interface my account success")
                self.device.press.back()
                return True
        else:
            self.device(text="Account").click()
            if self.device(text="Payment methods").wait.exists():
                self.logger.info("Check interface my account success")
                self.device.press.back()
                return True
        self.logger.info("Check interface my account success")
        self.save_fail_img()
        self.back_main_app()
        return False

    def check_setting(self):
        self.logger.info("Check interface setting")
        self.back_main_app()
        self.device(description="Show navigation drawer").click.wait()
        self.device(scrollable=True).scroll.vert.toEnd()
        self.device(text="Settings").click()
        if self.device(text="Auto-update apps").wait.exists(timeout=5000):
            self.logger.info("Check interface setting success")
            self.device.press.back()
            return True
        else:
            self.logger.info("Check interface setting success")
            self.save_fail_img()
            self.back_main_app()
            return False

    def click_open_if_exists(self):
        if self.device(textMatches="Open|OPEN").wait.exists(timeout=3000):
            self.logger.info("found Open, click")
            self.device(textMatches="Open|OPEN").click()
            self.device.delay(2)
            return True
        return False

    def click_install_if_exists(self):
        if self.install_node.wait.exists(timeout=3000):
            self.logger.info("found Install, click")
            self.install_node.click()
            self.device.delay(2)
            if self.device(text="CONTINUE").exists:
                self.device (text="CONTINUE").click()
                self.device.delay (3)
            if self.device(text="Skip").exists:
                self.device (text="Skip").click()
            return True
        return False

    def click_unistall_if_exists(self):
        if self.uninstall_node.wait.exists(timeout=3000):
            self.logger.info("found Uninstall, click")
            self.uninstall_node.click()
            self.device.delay(1)
            self.click_ok_if_exists()
            return True
        return False

    def click_ok_if_exists(self):
        if self.device(text="OK").wait.exists(timeout=3000):
            self.device(text="OK").click()
            self.device.delay(1)

    def click_cancel_if_exists(self):
        if self.device(text="App optimization").wait.exists(timeout=3000):
            if self.device(resourceId="com.tct.onetouchbooster:id/apop_dialog_checkbox").exists:
                self.device(resourceId="com.tct.onetouchbooster:id/apop_dialog_checkbox").click()
                self.device.delay(1)
            if self.device(text="CANCEL").exists:
                self.device(text="CANCEL").click()
                self.device.delay(1)

    def download_open_apk(self, apk="Google Authenticator"):
        self.logger.info("download and open apk %s" % apk)
        self.logger.info("search %s apk" % apk)
        self.playstore_home.click.wait()
        self.device(resourceId="com.android.vending:id/search_bar_text_input").set_text(apk.lower())
        self.device.press.enter()
        # verify if downloaded already
        if self.device(text="Open").wait.exists(timeout=3000):
            # x, y = 491, 411
            # self.device.click(x, y)
            self.device(text=apk).click()
            if self.device(text="Auto-start").exists:
                self.device.delay(2)
                self.device(text="CANCEL").click()
            self.click_unistall_if_exists()
            self.device.delay(5)  # wait to uninstall
            self.device.press.back()

        # install
        assert self.click_install_if_exists(), 'can not find install icon'

        # wait install
        assert self.device(resourceId="com.android.vending:id/right_button", text="Cancel").wait.gone(
            timeout=60000), "Apk did not download successfully within 30 seconds"

        # verify install
        assert self.click_open_if_exists(), 'can not find open icon, install fail or timeout'
        self.click_cancel_if_exists()
        self.click_ok_if_exists()

        self.device.delay(2)
        if self.device(packageName="com.android.vending").exists:
            self.save_fail_img()
            self.logger.error("******* downloading do not finish within 60s ******")
            return False

        for i in range(3):
            self.device.press.back()
            self.device.delay()
            if self.open_node.wait.exists(timeout=3000):
                self.device (text=apk).click ()
                # x, y = 491, 411
                # self.device.click(x, y)
                self.click_unistall_if_exists()
                self.device.delay(5)  # wait to uninstall
                break


        if self.install_node.wait.exists(timeout=10000):
            self.logger.info("uninstall %s apk success" % apk)
            return True
        else:
            self.logger.info("uninstall %s apk failed" % apk)
            self.save_fail_img()
            return False

    def verify_account_login(self, account):
        """
        check the account is shown after Google account enrolled
        :param account:
        :return:
        """
        self.open_menu()
        assert self.device(text=account).wait.exists(), "******** %s do not login  ********"

    def open_menu(self):
        """
        open play store menu
        :return:
        """
        assert self.back_main_app(), "can not back to play store home screen"

        self.device(description="Show navigation drawer").click()
        self.device(description="Show navigation drawer").wait.gone(timeout=3000)

        # verify
        assert self.device(resourceId="com.android.vending:id/play_drawer_list").wait.exists(
            timeout=3000), "play store menu do not opened"

    def select_auto_update(self, option="Do not auto-update apps"):
        """
        select auto update, generally set it to do not update
        :return:
        """
        self.open_menu()
        self.device(scrollable=True, resourceId="com.android.vending:id/play_drawer_list").scroll.vert.toEnd()
        self.device(text="Settings").click()

        # open Auto-update apps
        auto_update_apps = self.device(text="Auto-update apps")
        assert auto_update_apps.wait.exists(timeout=5000), "**** can not find Auto-update apps menu"
        auto_update_apps.click()

        # select option
        item_to_select = self.device(text=option)
        item_to_select2 = self.device(text="Do not auto-update apps.")
        # assert item_to_select.wait.exists() or item_to_select2.exists, "******** can not find option: %s  ********" % option
        if item_to_select.wait.exists():
            item_to_select.click.wait(timeout=3000)
        else:
            item_to_select2.click.wait(timeout=3000)

        # verify
        assert auto_update_apps.wait.exists(timeout=2000), "can not back to Auto-update apps after selected option"


if __name__ == '__main__':
    a = PlayStore("80c08ac6", "PlayStore")
    a.enter()
    a.download_open_apk()
    a.back_main_app()
