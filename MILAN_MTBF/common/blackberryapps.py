# -*- coding: utf-8 -*-

from common import *


class BlackBerryApps(Common):
    """Provide common functions involved Calendar."""

    def enter_dtek(self):
        '''Launch calender by start activity.
        '''
        if self.device(resourceId="com.blackberry.privacydashboard:id/gauge").wait.exists(timeout=3000):
            self.logger.debug("DTEK is already open successfully.")
            return True
        self.start_app("DTEK by BlackBerry")
        if self.device(resourceId="com.blackberry.privacydashboard:id/gauge").wait.exists(timeout=5000):
            self.logger.debug("Open DTEK successfully.")
            return True
        self.logger.debug("Open DTEK failed.")
        return False

    def enter_Preview(self):
        '''Launch calender by start activity.
        '''
        if self.device(resourceId="com.blackberrymobile.aota:id/fab",
                       packageName="com.blackberrymobile.aota").wait.exists(
            timeout=5000):
            self.logger.debug("BlackBerry Help(Preview) is already open successfully.")
            return True
        self.start_app("Preview")
        if self.device(text="NEXT STEP").ext5:
            self.device(text="NEXT STEP").click()

        if self.device(text="Settings").ext5:
            self.device(text="Settings").click()

        if self.device(resourceId="com.blackberrymobile.aota:id/fab",
                       packageName="com.blackberrymobile.aota").wait.exists(
            timeout=5000):
            self.logger.debug("Open BlackBerry Help(Preview) successfully.")
            return True
        self.logger.debug("Open BlackBerry Help(Preview) failed.")
        return False

    def enter_productivityEdge(self):

        for loop in range(5):
            self.device.delay(3)
            self.device.swipe(1070, 760, 500, 760, 20)
            if self.device(resourceId="com.blackberry.productivityedge:id/tabIcon").wait.exists(timeout=3000):
                self.logger.debug("open productivityEdge successfully.")
                return True
        self.logger.debug("Open productivityEdge failed.")
        return False

    def enter_DeviceSearch(self):
        '''Launch calender by start activity.
        '''
        if self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").wait.exists(
                timeout=3000):
            self.logger.debug("Device Search is already open successfully.")
            return True
        self.start_app("Device Search")
        if self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").wait.exists(
                timeout=5000):
            self.logger.debug("Open Device Search successfully.")
            return True
        self.logger.debug("Open Device Search failed.")
        return False

    def enter_PasswordKeeper(self, password):
        '''Launch calender by start activity.
        '''

        # if self.device(resourceId="com.blackberry.help:id/spinner_title", text="BlackBerry Help").wait.exists():
        # self.logger.debug("BlackBerry Help is already open successfully.")
        # return True
        self.start_app("Password Keeper")
        # self.logger.info("password is :%s" % password)
        # self.adb.shell("adb shell input text password")
        # self.device.delay(2)
        # self.device.press.enter()

        if self.device(text="Password Keeper").wait.exists(timeout=5000):
            self.logger.debug("Open Password Keeper successfully.")
            return True
        self.logger.debug("Open Password Keeper failed.")
        return False

    def checkChangeSetting(self):
        self.logger.debug('starting to check the  Change Setting')
        self.enter_dtek()

        self.device(scrollable=True).scroll.vert.to(text="Unknown sources")
        self.device(text="Trusted app sites").click()

        if self.device(text="CHANGE SETTINGS").wait.exists(timeout=5000):
            self.logger.info("CHANGE SETTINGS exists.")
            self.device.press.back()
            self.device.press.back()
            return True
        self.logger.info("CHANGE SETTINGS not exists.")
        self.save_fail_img()
        return False

    def productivityEdgeSettingsTest(self):
        self.logger.info("start productivityEdgeSettings Test")
        self.enter_productivityEdge()
        if self.device(resourceId="com.blackberry.productivityedge:id/tabIcon", description="Settings").exists:
            self.device(resourceId="com.blackberry.productivityedge:id/tabIcon", description="Settings").click()
        if self.device(text="Left").exists:
            self.device(text="Left").click()
        if self.device(text="Right").wait.exists(timeout=5000):
            self.device(text="Right").click()

        tab_height = self.device(resourceId="com.blackberry.productivityedge:id/tabHeight")
        # self.logger.info(location)
        # left_location = self.device(resourceId="com.blackberry.productivityedge:id/tabHeight").get_left_location()
        # self.logger.info("left_location is %s" % left_location)

        info_bounds = tab_height.info["bounds"]
        right_location = info_bounds["right"]
        top_location = info_bounds["top"]
        bottom_location = info_bounds["bottom"]

        # right_location = self.device(resourceId="com.blackberry.productivityedge:id/tabHeight").get_right_location()
        # self.logger.info("right_location is %s" % str(right_location))
        #
        # top_location = self.device(resourceId="com.blackberry.productivityedge:id/tabHeight").get_top_location()
        # self.logger.info("right_location is %s" % str(right_location))
        #
        # bottom_location = self.device(resourceId="com.blackberry.productivityedge:id/tabHeight").get_bottom_location()
        # self.logger.info("right_location is %s" % str(right_location))

        # centerX = (right_location + left_location) / 2
        centerX_2 = right_location / 2
        centerX_3 = right_location / 3

        centerY = (top_location + bottom_location) / 2
        print "centerX_2:", centerX_2
        print "centerX_3:", centerX_3
        print "centerY:", centerY

        self.device.click(centerX_2, centerY)
        self.logger.info("set Height 'centerX/2' successfully!")
        self.device.delay(3)
        self.device.click(centerX_3, centerY)
        self.logger.info("set Height 'centerX/3' successfully!")

        if self.device(packageName="com.blackberry.productivityedge").wait.exists(timeout=5000):
            self.logger.info("Test productivityEdgeSettings successfully")
            return True

        self.logger.warning("Test productivityEdgeSettings failed")
        self.save_fail_img()
        return False

    def openEmailFromProductivityEdgeTest(self):
        '''openEmailFromProductivityEdgeTest
        '''
        self.logger.info("start open Email From ProductivityEdge Test")
        self.enter_productivityEdge()

        if self.device(description="BlackBerry Hub").wait.exists(timeout=5000):
            self.device(description="BlackBerry Hub").click()
        if self.device(description="hub").wait.exists(timeout=1000):
            self.device(description="hub").click.wait()

        if self.device(textContains="stability test with no attachment").wait.exists(timeout=120000):
            self.logger.info("email 'stability test with no attachment' exists")
            self.device(textContains="stability test with no attachment").click.wait()

            if self.device(description="Delete").wait.exists(timeout=5000):
                self.logger.info("Open email from ProductivityEdge successfully!")
                if self.device(description="Delete").wait.exists(timeout=5000):
                    self.device(description="Delete").click()

                if self.device(text="DELETE").wait.exists(timeout=5000):
                    self.device(text="DELETE").click()
                    self.logger.info("Delete email from ProductivityEdge successfully!")
                    return True

        self.logger.info("Can not found email from ProductivityEdge!")
        self.save_fail_img()
        return False

    def openTaskFromProductivityEdgeTest(self, name):
        '''openEmailFromProductivityEdgeTest
        '''
        self.logger.info("start open Task From ProductivityEdge Test")
        self.enter_productivityEdge()

        if self.device(description="calendar").wait.exists(timeout=5000):
            self.device(description="hub").click.wait()
            self.device.delay(2)
            self.device(description="tasks").click()

            if self.device(text=name).wait.exists(timeout=20000):
                self.device(text=name).click()
            else:
                self.logger.debug("sync task fail")
                self.save_fail_img()
                return False

            if self.device(resourceId="com.blackberry.tasks:id/menu_delete").wait.exists(timeout=5000):
                self.device(resourceId="com.blackberry.tasks:id/menu_delete").click()

            if self.device(text="DELETE").wait.exists(timeout=5000):
                self.device(text="DELETE").click()
                self.logger.info("delete the Task %s" % name)
            self.logger.info("Task Sync to ProductivityEdge Successfully!")
            return True
        self.logger.info("Task Sync to ProductivityEdge Fail!")
        self.save_fail_img()
        return False

    def gmailRemoteSearchTest(self):
        '''trying to open gmail account and search,
        if we do not see we are still in the hub, we have problem
        '''
        self.logger.info("start to open gmail account and search Test")

        if self.device(resourceId="com.blackberry.hub:id/search_menu_item").wait.exists(timeout=5000):
            self.device(resourceId="com.blackberry.hub:id/search_menu_item").click()

        if self.device(resourceId="android:id/search_src_text").wait.exists(timeout=5000):
            self.device(resourceId="android:id/search_src_text").set_text("somerandomstring")

        if self.device(text="Remote Search").wait.exists(timeout=5000):
            self.device(text="Remote Search").click()
            self.device.delay(3)
            if not self.device(packageName="com.blackberry.hub").wait.exists(timeout=5000):
                self.logger.warning("Hub Crashed during search 'somerandomstring'")
                return False

        self.logger.info("open email account and search Test successfully")
        return True

    def checkBatteryLevels(self):
        """check Battery Levels.
        """
        self.logger.debug("start to check Battery Levels.")
        if self.device(text="SETTINGS").wait.exists(timeout=5000):
            self.device(text="SETTINGS").click()
        self.device.swipe(500, 1500, 500, 500, 20)
        if self.device(text="Check your battery power level and usage info").wait.exists(timeout=5000):
            self.device(text="Check your battery power level and usage info").click()

        if self.device(text="TRY IT NOW").wait.exists(timeout=5000):
            self.device(text="TRY IT NOW").click()

        if self.device(text="Battery saver").wait.exists(timeout=5000):
            self.logger.info("switch to Battery successfully")
            self.device.press.back()
            return True

        self.logger.info("switch to Battery failed")
        self.save_fail_img()
        return False

    def searchForContactTest(self):
        '''searchForContactTest
        '''
        self.logger.info("start to Search For Contact Test")
        self.enter_DeviceSearch()
        el = self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text")
        if el.wait.exists(timeout=5000):
            el.set_text("AutoTest01")
            self.device.delay(5)
        el1 = self.device(resourceId="com.blackberry.universalsearch:id/card_layout").child(textStartsWith="AutoTest01")
        el2 = self.device(resourceId="com.blackberry.universalsearch:id/text_1", textStartsWith='AutoTest01')
        for i in range(3):
            self.logger.info("try %s times to click contact searched out" % i)
            if el1.wait.exists(timeout=10000):
                el1.click()
            elif el2.wait.exists(timeout=10000):
                el2.click()
            self.device.delay(10)

            if self.device(textStartsWith="AutoTest01").wait.exists(timeout=5000) and \
                    (self.device(text="10010").wait.exists() or self.device(text="10000").wait.exists() or self.device(
                        text="10086").wait.exists()):
                self.logger.info("Search for contact  AutoTest01 Successfully!")
                return True

        self.logger.info("Search for contact  AutoTest01 fail!")
        self.save_fail_img()
        return False

    def searchCallContactTest(self):
        '''searchForContactTest
        '''
        self.logger.info("start to Search For Call Contact Test")
        self.enter_DeviceSearch()
        if self.device(description="Clear search term").exists:
            self.device(description="Clear search term").click.wait()
        if self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").wait.exists(timeout=5000):
            self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").set_text("Call AutoTest01")

        if self.device(resourceId="com.blackberry.universalsearch:id/text_1",
                       textStartsWith="Call AutoTest01").wait.exists(
                timeout=5000):
            self.device(resourceId="com.blackberry.universalsearch:id/text_1", textStartsWith="Call AutoTest01").click()

        if self.device(description="End call").wait.exists(timeout=10000):
            self.logger.info("Search For Call Contact  AutoTest01 successfully!")
            return True

        self.logger.info("Search For Call Contact AutoTest01 fail!")
        self.save_fail_img()
        return False

    def deviceSearchCrashBySearchedCharacterTest(self):
        '''searchForContactTest
        '''
        self.logger.info("Start to  Search Crash By SearchedCharacter Test")
        self.enter_DeviceSearch()

        for loop in range(32, 126):
            testCharacter = chr(loop)
            if self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").wait.exists(timeout=5000):
                self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").set_text(testCharacter)
                self.logger.debug("Type '%s' successfully!" % testCharacter)

            if not self.device(packageName="com.blackberry.universalsearch").wait.exists(timeout=5000):
                self.logger.error("Device search app crashed or got closed after typing %s" % testCharacter)
                self.save_fail_img()
                return False
            if self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").wait.exists(timeout=5000):
                self.device(resourceId="com.blackberry.universalsearch:id/search_edit_text").clear_text()

        self.logger.info("Search Crash By SearchedCharacter Test Successfully")
        return True

    def vkbSwipeToDeleteInHubTest(self):
        '''searchForContactTest
        '''
        self.logger.info("start to  Swipe To Delete In Hub Test")

        if self.device(description="Compose button").wait.exists(timeout=5000):
            self.device(description="Compose button").click.wait()

        if self.device(scrollable=True).wait.exists():
            self.device(scrollable=True).scroll.vert.to(resourceId="com.blackberry.hub:id/subjectField")

        if self.device(resourceId="com.blackberry.hub:id/subjectField").wait.exists(timeout=5000):
            self.device(resourceId="com.blackberry.hub:id/subjectField").set_text("Hello how are you")
            self.device.delay(2)
            # self.adb.shell("input text 'Hello how are you '")

        # get Screen resolution, if it is larger, add some pixel
        displayHeight = self.device.info["displayHeight"]
        self.logger.debug("displayHeight = %s" % displayHeight)
        displayHeight = displayHeight / 5 * 4

        if self.device(text="Hello how are you").wait.exists(timeout=5000):
            self.logger.info("set text 'Hello how are you' successfully!")
            for loop in range(4):
                self.logger.info("delete a word through swipe VirtualKeyboard !")
                self.device.swipe(900, displayHeight, 400, displayHeight, 1)
                self.device.delay(1)

        if not self.device(text="Hello how are you").wait.exists(timeout=5000):
            self.logger.info("Swipe To Delete word in hub successfully!")

            if self.device(description="Navigate up").wait.exists(timeout=5000):
                self.device(description="Navigate up").click()

            if self.device(text="DISCARD").wait.exists(timeout=5000):
                self.device(text="DISCARD").click()
            return True

        if self.device(description="Navigate up").wait.exists(timeout=5000):
            self.device(description="Navigate up").click()

        if self.device(text="DISCARD").wait.exists(timeout=5000):
            self.device(text="DISCARD").click()

        self.logger.info("Swipe To Delete word in hub fail!")
        self.save_fail_img()
        return False


if __name__ == '__main__':
    a = BlackBerryApps("35b9a80f", "Schedule")
    a.productivityEdgeSettingsTest()
