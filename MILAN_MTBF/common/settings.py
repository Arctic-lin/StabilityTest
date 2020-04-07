# -*- coding: UTF-8 -*-
"""Settings library for scripts.
"""
import sys
import time
import traceback

from chrome import Chrome
from common import Common
from ui_parser import UIParser

reload(sys)
sys.setdefaultencoding("utf-8")
# from browser import Browser


class Settings(Common):
    """Provide common functions involved wifi,display,sound etc."""
    app_name = 'Settings'
    package = 'com.android.settings'
    launch_activity = '.Settings'
    network_text = "Cellular network"

    def __init__(self, device, log_name, sdevice=None):
        Common.__init__(self, device, log_name, sdevice)
        self.screen_lock_pwd = "1234"

    def enter_settings(self, option):
        '''enter the option of settings screen
         argv: the text of the settings option
        '''
        self.logger.debug("starting to enter System")
        self.start_app(self.app_name)
        self.device(scrollable=True).scroll.vert.to(text=option)
        if self.device(text=option).wait.exists(timeout=10000):
            self.device(text=option).click()
            return True
        else:
            return False

    def switch_network_for_multi_menus(self, network_type):
        """
        Mercury O and Athena they have same OS, but the path to enter network type is different,
        this is a common method to select network type
        Network & Internet->Mobile network->Advanced->Preferred network type
        Network & Internet->Cellular networks->Preferred network type
        :param network_type:
        :return:
        """
        # current network type mismatch
        # do nothing with this for now
        # lte/wcdma 			global
        # lte 					cdma/evdo/gsm/wcdma
        # global 				gsm/wcdma/lte
        # gsm/wcdma 			lte/wcdma
        # cdma + lte/evdo 		wcdma preferred
        # cdma/evdo/gsm/wcdma 	gsm/wcdma/lte
        # evdo only 			wcdma preferred
        # cdma w/o evdo 		lte
        # cdma/evdo auto 		wcdma only
        # gsm/wcdma auto		tdscdma
        # wcdma 				lte/wcdma
        # gsm only				lte
        # gsm/wcdma preferred 	global

        network_mapping = {
            # '2G': 'GSM only',
            # '3G': 'GSM/WCDMA auto',
            # 'ALL': 'GSM/WCDMA/LTE',
            '2G': '2G',
            '3G': '3G/2G',
            'ALL': '4G/3G/2G',
        }
        if not self.get_carrier_service_num():
            self.logger.error('no sim card skip network switch')
            return False
        try:
            self.logger.debug('Switch network to {}:{}.'.format(network_type, network_mapping[network_type]))
            self.enter_settings('Network & internet')
            network_type = network_mapping[network_type]
            steps = ['Cellular network',
                     # 'Advanced',
                     'Preferred network type',
                     ]
            for step in steps:
                el = self.device(text=step)
                if el.exists:
                    el.click()
                    self.device.wait.idle()
            # self.device(scrollable=True).scroll.vert.to(text=network_type)
            el = self.device(text=network_type)  # 2G, 3G/2G, 4G/3G/2G
            if el.exists:
                el.click.wait()
            # comment assert for now
            # self.device.delay(20)
            # assert self._is_connected(network_type)
            self.logger.debug('Switch network to {} successfully'.format(network_type))
        except:
            self.logger.warning(traceback.format_exc())
            self.save_fail_img()
        finally:
            self.back_to_home()

    def switch_network(self, type=""):
        """
        switch network to specified type.
        Android O: settings -> Networe & Internet -> Mobile network -> Preferred network type
                    4G/3G/2G
                    3G/2G
                    2G
        :param type: the type of network.
        :return:
        """
        try:
            network_type = self.appconfig(type, "Settings")
            self.logger.debug("Switch network to %s:%s." % (type, network_type))
            if self.enter_settings(self.appconfig("networks", "Settings")):
                connect = [
                    {"id": {"text": self.appconfig("Mobile_network", "Settings")}},
                    {"id": {"text": "Advanced"}},
                    {"id": {"text": "Preferred network type"}},
                    {"id": {"text": network_type}},
                ]
                if not UIParser.run(self, connect):
                    self.save_fail_img()
                    return False
            else:
                return False
            print self._is_connected(type)
            self.back_to_home()
        except:
            self.logger.warning(traceback.format_exc())
            self.save_fail_img()

    def login_google_account(self, account="tclooa@gmail.com", pwd="qazwsx.edc", remove_logged_account=True):
        """
        login in Google account from settings
        :param accout: 
        :param pwd: 
        :return: 
        """
        self.enter_settings("Users & accounts")
        # check account logged in or not, remove it if need
        if self.device(text="Google").wait.exists(timeout=5000):
            self.device(text="Google").click.wait()
            if self.device(text=account).wait.exists(timeout=5000):
                if remove_logged_account:
                    # assert self.device(description="More options").wait.exists(), "******** can not find menu btn  ********"
                    # self.device(description="More options").click.wait(timeout=3000)
                    assert self.device(
                        text="REMOVE ACCOUNT").wait.exists(), "******** can not find remove account btn  ********"
                    self.device(text="REMOVE ACCOUNT").click.wait(timeout=3000)
                    assert self.device(
                        text="REMOVE ACCOUNT").wait.exists(), "******** can not find remove account btn  ********"
                    self.device(text="REMOVE ACCOUNT").click.wait(timeout=3000)
                else:
                    self.logger.info("%s has logged in" % account)
                    return True

        assert self.device(text="Add account").wait.exists(), "******** can not find add account btn  ********"
        self.device(text="Add account").click.wait(timeout=3000)

        self.device(scrollable=True).scroll.vert.to(text="Google")
        self.device.delay(1)
        assert self.device(text="Google").wait.exists(), "******** can not find Google btn  ********"
        self.device(text="Google").click.wait(timeout=3000)

        # input account #20180728 gms变更，text不存在，换成resourceid定位
        # assert self.device(text="Email or phone").wait.exists(timeout=60 * 1000), "******** can not find Google account setupwizard after 60s  ********"
        # self.device(text="Email or phone").set_text(account)

        assert self.device(resourceId="identifierId").wait.exists(
            timeout=60 * 1000), "******** can not find Google account setupwizard after 60s  ********"
        self.device(resourceId="identifierId").set_text(account)

        assert self.device(resourceId="identifierNext").ext5
        self.device(resourceId="identifierNext").click()

        # input pwd  #20180728 gms变更，text不存在，换成className定位
        # assert self.device(text="Enter your password").wait.exists(timeout=60 * 1000), "******** can not find pw input textbox after 60s  ********"
        # self.device(text="Enter your password").set_text(pwd)

        # assert self.device(className="android.widget.EditText").wait.exists(timeout=60 * 1000), "******** can not find pw input textbox after 60s  ********"
        # self.device(className="android.widget.EditText").click()
        # self.device(className="android.widget.EditText").set_text(pwd)

        self.device.dump()
        if self.device(className="android.widget.EditText").wait.exists(timeout=30000):
            self.device(className="android.widget.EditText").click()
            self.device.dump()
            time.sleep(3)
            self.device(className="android.widget.EditText").set_text(pwd)
            # self.adb.shell("input text %s"%gmail[1])
            self.logger.debug("input password %s" % pwd)

        self.device.delay(1)
        self.device(resourceId="passwordNext").click()

        if self.device(text="I agree").wait.exists(timeout=2000):
            self.device(text="I agree").click.wait()
        self.device.wait.idle()
        self.device.dump()
        for loop in range(5):
            if self.device(text="MORE", resourceId="com.google.android.gms:id/next_button").exists:
                self.device(text="MORE", resourceId="com.google.android.gms:id/next_button").click.wait()
                self.logger.debug("click MORE")
                continue
            if self.device(textContains="ACCEPT", resourceId="com.google.android.gms:id/next_button").exists:
                self.device(textContains="ACCEPT", resourceId="com.google.android.gms:id/next_button").click.wait()
                break
            time.sleep(3)

        # confirm Google account was logged in
        assert self.device(text=account).ext5, "******** can not find Google btn after Google account added ********"

        return None

    def _check_account_logged_in(self, account, remove_logged_account):
        if self.device(text="Google").wait.exists(timeout=2000):
            self.device(text="Google").click.wait()
            if self.device(text=account).wait.exists(timeout=2000):
                if remove_logged_account:
                    assert self.device(
                        description="More options").wait.exists(), "******** can not find menu btn  ********"
                    self.device(description="More options").click.wait(timeout=3000)
                    assert self.device(
                        text="Remove account").wait.exists(), "******** can not find remove account btn  ********"
                    self.device(s_text="Remove account").click.wait(timeout=3000)

    def enable_dev_mode(self):
        """
        enable about phone via press Build number 7 times
        :return:
        """
        self.enter_settings("System")
        if self.device(scrollable=True).wait.exists():
            self.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)
        self.device(text="About phone").click.wait()
        self.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)

        build_num = self.device(text="Build number")
        assert build_num.wait.exists(), "******** can not find Build number  ********"
        for i in range(7):
            build_num.click()
            self.device.delay(0.5)

        self.device.press.back()
        if not self.device(text="Developer options").wait.exists():
            self.device.press.back()

        assert self.device(text="Developer options").wait.exists(), "******** developer options do not opened  ********"
        return True

    def switch_unknown_sources(self, switchState):
        self.logger.debug('starting to %s unknown sources' % switchState)
        self.enter_settings("Security")
        self.device(scrollable=True).scroll.vert.to(text="Unknown sources")

        for loop in range(9):
            self.logger.info("get 'unknown sources' %s times" % str(loop + 1))
            if self.device(resourceId="com.android.settings:id/list").child(
                    className="android.widget.LinearLayout", index=loop).child(
                className="android.widget.RelativeLayout").child(resourceId="android:id/title").exists:
                title_text = self.device(resourceId="com.android.settings:id/list").child(
                    className="android.widget.LinearLayout", index=loop).child(
                    className="android.widget.RelativeLayout").child(resourceId="android:id/title").get_text()

                if title_text == "Unknown sources":
                    switch_widget = self.device(resourceId="com.android.settings:id/list").child(
                        className="android.widget.LinearLayout", index=loop).child(
                        className="android.widget.LinearLayout").child(resourceId="android:id/switch_widget")
                    switch_text = switch_widget.get_text()
                    self.logger.info('get Unknown sources successfully,switch_text is %s' % switch_text)

                    if switchState == "open":
                        if switch_text == "ON":
                            self.logger.debug('unknown sources is already opened')
                        if switch_text == "OFF":
                            switch_widget.click()
                            if self.device(text="OK").exists:
                                self.device(text="OK").click()
                        if switch_widget.get_text() == "ON":
                            self.logger.debug('open unknown sources successfully')
                            return True

                    if switchState == "close":
                        if switch_text == "OFF":
                            self.logger.debug('unknown sources is already closed')
                        if switch_text == "ON":
                            switch_widget.click()

                        if switch_widget.get_text() == "OFF":
                            self.logger.debug('close unknown sources successfully')
                            return True

        self.logger.debug('%s unknown sources failed' % switchState)
        return False

    def switch_screen_lock_between_pin_and_none(self):
        """
        set screen lock with the given pin
        :return:
        """
        self.logger.debug('set screen lock with pin code %s' % self.screen_lock_pwd)
        self.enter_settings("Location")

        self.open_screen_lock_menu()

    def revert_screen_lock_pin(self):
        """
        revert screen lock pin
        :return:
        """

    def get_current_screen_lock(self):
        """
        get current screen lock, None, Swipe, Pattern, PIN or Password
        :return:
        """
        assert self._is_screen_lock_activity(), "******** do not in choose screen lock activity  ********"
        content = self.device(resourceId="com.android.settings:id/list")
        child_count = content.info["childCount"]
        print child_count

        current_lock = "unknown"
        for i in range(child_count):
            if content.child(index=i).child(index=0).child(text="Current screen lock").exists:
                current_lock = content.child(index=i).child(index=0).child(index=1).child(index=0).get_text()
                return current_lock
            continue
        return current_lock

    def open_screen_lock_menu(self):
        screen_lock = self.device(text="Screen lock")
        assert screen_lock.wait.exists(), "******** can not find screen lock item in settings ********"
        screen_lock.click.wait(timeout=3000)

        # input pwd if need
        if self.device(resourceId="com.android.settings:id/password_entry").wait.exists(timeout=3000):
            self.device(resourceId="com.android.settings:id/password_entry").set_text(self.screen_lock_pwd)
            self.device.delay(1)
            self.device.press.enter()

        assert self._is_screen_lock_activity(), "******** open screen lock menu failed  ********"

    def _is_screen_lock_activity(self):
        return self.device(text="Choose screen lock").wait.exists()

    def enableProductivityEdge(self, isEnable):
        if isEnable:
            self.logger.debug('starting to enable ProductivityEdge')
        else:
            self.logger.debug('starting to disable ProductivityEdge')
        self.enter_settings("Display")

        if self.device(text="Advanced").wait.exists(timeout=3000):
            self.device(text="Advanced").click.wait()

        self.device(scrollable=True).scroll.vert.toEnd()

        p_switch_el = self.device(text='Productivity Tab').right(resourceId='android:id/switch_widget')
        p_switch_text = p_switch_el.get_text()

        if isEnable:
            if p_switch_text == "OFF":
                p_switch_el.click()
                self.device.delay(2)
            productivity_text = p_switch_el.get_text()
            if productivity_text == "ON":
                self.logger.debug('open ProductivityEdge successfully')
                return True
            self.logger.debug('open ProductivityEdge failed')
            return False
        else:
            if p_switch_text == "ON":
                p_switch_el.click()
                self.device.delay(2)
            productivity_text = p_switch_el.get_text()
            if productivity_text == "OFF":
                self.logger.debug('close ProductivityEdge successfully')
                return True
            self.logger.debug('close ProductivityEdge failed')
            return False

    def enableVirtualKeyboard(self):
        self.logger.debug('starting to open VirtualKeyboard')
        return self._switch_verturl_keyboard("ON")

    def disableVirtualKeyboard(self):
        self.logger.debug('starting to disable VirtualKeyboard')
        return self._switch_verturl_keyboard("OFF")

    def _switch_verturl_keyboard(self, trigger):
        self.enter_settings("System")
        if self.device(text="Languages & input").wait.exists(timeout=5000):
            self.device(text="Languages & input").click.wait()
        if self.device(text="Physical keyboard").wait.exists(timeout=5000):
            self.device(text="Physical keyboard").click.wait()

        show_vkb_content = self.device(text="Show virtual keyboard")
        assert show_vkb_content.exists, "Can't find the text - Show virtual keyboard"

        switch_button = show_vkb_content.right(resourceId="android:id/switch_widget")
        if switch_button.get_text() == trigger:
            self.logger.debug('VirtualKeyboard is already %s' % trigger)
            return True
        else:
            switch_button.click.wait()
            self.logger.debug('switch VirtualKeyboard successfully')
            return True

        self.logger.debug('%s VirtualKeyboard failed' % trigger)
        return False

    def search_in_settings(self, tar_str):
        self.back_to_home()
        self.start_app("Settings")
        self.device.wait("idle")
        self.device(resourceId="com.android.settings:id/search_action_bar").click.wait()
        if self.device(resourceId="android:id/search_src_text").wait.exists():
            self.device(resourceId="android:id/search_src_text").set_text(tar_str)
            self.device.wait("idle")


class Wifi(Settings):
    def __init__(self, device, log_name, sdevice=None):
        Settings.__init__(self, device, log_name, sdevice)
        self.chrome = Chrome(self.device, "wifi_chrome")
        # self.browser = Browser(self.device, "wifi_browser")
        # in wifi list activity, settings->Network & internet->Wi-Fi
        self.wifi_switch = self.device(resourceId='com.android.settings:id/switch_widget')


    def open_wifi(self):
        try:
            self.enter()
            self.open()
        except:
            self.logger.warning(traceback.format_exc())
        self.logger.info("open wifi completed")

    def enter(self):
        '''enter wifi settings
            Wi‑Fi
            Wi-Fi
        '''
        if self.enter_settings('Network & internet'):
            wifi = self.device(text="Wi-Fi")
            if not wifi.wait.exists():
                wifi = self.device(text="Wi‑Fi")
            assert wifi.wait.exists(), "Can't find Wi-Fi!"
            wifi.click.wait()
            return self.wifi_switch.wait.exists()
        return False

    def back_to_wifi(self):
        '''back to wifi list
         argv: 
        '''
        self.logger.debug('Back to Wi-Fi list')
        for loop in range(5):
            if self.wifi_switch.exists:
                return True
            self.device.press.back()
            self.device.delay(1)
        return False

    def open(self):
        '''validate wifi open status
         argv: To see available networks -- close
               wifi list -- open
        '''
        self.logger.debug('Open wifi')
        if self.device(textMatches="Off|OFF", resourceId="com.android.settings:id/switch_text").wait.exists(timeout=5000):
            self.device(textMatches="Off|OFF", resourceId="com.android.settings:id/switch_text").click()
            self.logger.debug('close wifi clicked')
        if self.device(textMatches="On|ON", resourceId="com.android.settings:id/switch_text").wait.exists(timeout=10000):
            self.logger.debug('wifi close pass.')
            return True
        self.logger.debug('wifi open fail!!!')
        self.device.delay(5)
        return False

    def close(self):
        '''validate wifi close status
         argv: To see available networks -- closed
               wifi list -- open
        '''
        self.logger.debug('Close wifi')
        if self.device(textMatches="On|ON", resourceId="com.android.settings:id/switch_text").wait.exists(timeout=5000):
            self.device(textMatches="On|ON", resourceId="com.android.settings:id/switch_text").click()
            self.logger.debug('close wifi clicked')
        if self.device(textMatches="Off|OFF", resourceId="com.android.settings:id/switch_text").wait.exists(timeout=10000):
            self.logger.debug('wifi close pass.')
            return True
        self.logger.debug('wifi close fail!!!')
        self.device.delay(5)
        return False

        # if self.device(text="ON", resourceId="com.android.settings:id/switch_widget").wait.exists(timeout=5000):
        #     self.device(text="ON", resourceId="com.android.settings:id/switch_widget").click()
        #     self.logger.debug('close wifi clicked')
        # if self.device(text="OFF", resourceId="com.android.settings:id/switch_widget").wait.exists(timeout=10000):
        #     return True
        # self.logger.debug('wifi close fail!')
        # return False

    def connect_wifi(self, hotspot, password, security="", ):
        try:
            self.enter()
            self.open()
            self._connect(hotspot, password, security)
            self.back_to_home()
            return True
        except:
            self.logger.warning(traceback.format_exc())
            self.save_fail_img()
            return False

    def disconnect_wifi(self, hotspot):
        self.enter()
        # self.forget(hotspot)
        self.close()
        self.back_to_home()

    def _connect(self, hotspot, password, security="", enter=False):
        '''device connect wifi hotspot
         argv: (str)hotspotName -- the wifi hotspot's name 
               (str)password -- the wifi hotspot's password
               (str)security -- the password type
        '''
        self.logger.debug('Add hotspot --> ' + hotspot)
        if enter:
            self.enter()
        self.open()

        # if already connected, return
        if self.device(textStartsWith="Connected").wait.exists(timeout=3000):
            self.logger.debug('wifi connect success!!!')
            return True
        try:
            # if More options have add network option, you can use this option to add wifi
            if self.device(scrollable=True).wait.exists(timeout=2000):
                self.device(scrollable=True).scroll.vert.to(text="Add network")
            # self.device(description="More options").click()
            self.device(text="Add network").click.wait(timeout=2000)
            self.logger.debug("Input SSID/PWD/Security")
            if self.device(resourceId="com.android.settings:id/ssid").wait.exists(timeout=self.timeout):
                self.device(resourceId="com.android.settings:id/ssid").set_text(hotspot)
                if security != "":
                    self.logger.debug("Select security")
                    self.device(resourceId="com.android.settings:id/security").click()
                    self.device(text=security).click.wait(timeout=2000)
                    self.device.delay(1)
                if password != "":
                    self.device(resourceId="com.android.settings:id/password").set_text(password)
                    self.device.delay(1)
            self.logger.info(self.appconfig("wifi_connect", "Settings"))
            # self.device(textMatches='save|SAVE').click.wait(timeout=2000)
            # self.device(text='SAVE').click()
            self.device.delay(2)
            if self.device(text="SAVE").ext5:
                self.device(text="SAVE").click()
            else:
                self.click_text_SAVE()
            self.device.delay()
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
            if self.device(textStartsWith="Connected").wait.exists(timeout=80000):
                self.logger.debug('wifi connect success!!!')
                self.device.delay(1)
                return True
            elif self.device(text="Connected, no Internet").wait.exists(timeout=80000):
                self.logger.debug('wifi connect success!!!')
                self.device.delay(1)
                return True
            else:
                self.logger.debug('can not find hotspot: %s', hotspot)
                return False
        except:
            self.save_fail_img()
            self.logger.warning(traceback.format_exc())

    def forget(self, hotpot):
        '''device forget wifi hotpot
         argv: (str)hotpotName -- the wifi hotpot's name 
        '''
        self.logger.debug('forget hotpot')
        self.logger.debug('Search hotpot-------> ' + hotpot)
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
            self.device(scrollable=True).scroll.vert.to(text=hotpot)
        if self.device(text=hotpot).wait.exists(timeout=30000):
            self.device(text=hotpot).click()
            if self.device(text="FORGET").wait.exists(timeout=2000):
                self.device(text="FORGET").click()
                if self.device(text="Connected").wait.gone(timeout=3000):
                    self.device.delay(1)
                    return True
                else:
                    self.logger.info("forget hotpot %s failed" % hotpot)
                    self.save_fail_img()
                    return False
            else:
                self.logger.info(hotpot + ' is not connected!!!')
                self.device.press.back()
                return True

    def open_quick_wifi(self, ssid):
        self.device.open.quick_settings()
        self.device.delay(15)
        if self.device(text=ssid).wait.exists(timeout=1000*60):  # 自动有时候连接的很慢
            self.logger.info("wifi is connected to %s" % ssid)
            return True
        else:
            self.logger.info("wifi is off, open wifi from quick setting and connect %s" % ssid)
            wifi_ids = [self.device(description="Wi‑Fi Off,Open Wi-Fi settings."),
                        self.device(description="Wi‑Fi,"),
                        self.device(description="Wi-Fi,")]
            for wifi_id in wifi_ids:
                if wifi_id.exists:
                    # wifi_id.child(index=0).click()
                    wifi_id.click ()
                    break
            else:
                self.logger.error("******* wifi_ids not found ******")
                self.save_fail_img()
                return False

            # verify
            if self.device(text=ssid).wait.exists(timeout=30000):
                self.logger.debug("Wi-Fi is on, connect %s success" % ssid)
                return True
            elif self.device(description="Wi-Fi,").wait.exists(timeout=1000):   # WD, check wifi in another way
                text = self.device(description="Wi-Fi,").get_text()
                if text == 'On':
                    return True

            else:
                self.logger.debug("open wifi fail!!!")
                self.save_fail_img()
                return False

    def close_quick_wifi(self, ssid):
        self.device.open.quick_settings()
        self.device.delay()
        if self.is_wifi_off_in_quicksetting():
            return True
        else:
            self.logger.info("wifi is on, close wifi from quick setting and disconnect %s" % ssid)
            if self.device(descriptionContains=ssid).exists:
                self.device(descriptionContains=ssid).child(index=0).click()
            elif self.device(description='Wi-Fi three bars.').exists:
                self.device(description='Wi-Fi three bars.').click()
            elif self.device(description='Wi-Fi signal full.').exists:
                self.device(description='Wi-Fi signal full.').click()
            elif self.device(description="Wi-Fi disconnected.").exists:
                self.device(description="Wi-Fi disconnected.").click()
            else:
                self.device(text=ssid).click()
                self.device.delay(1)
                if self.device(text="ON").exists:
                    self.device(text="ON").click()
        # verify
        if self.is_wifi_off_in_quicksetting():
            self.logger.debug("close wifi success")
            return True
        else:
            self.logger.debug("close wifi fail!!!")
            self.save_fail_img()
            return False

    def is_wifi_off_in_quicksetting(self):
        wifi_ids = [self.device(description="Wi‑Fi Off, Open Wi-Fi settings."),
                    self.device(description="Wi‑Fi,"),
                    self.device(description="Wi-Fi,")]
        for wifi_id in wifi_ids:
            if wifi_id.exists:
                self.logger.info("wifi is off")
                return True
        else:
            self.logger.info("can't find wifi id")
        return False

    def web_refresh(self):
        '''switch wifi in quick settings panel and refresh website
        '''
        self.device.press.home()
        self.start_app("Chrome")
        self.chrome.home()
        self.chrome.browser_webpage(self.appconfig('web_page_download', "Chrome"))
        for loop in range(4):
            self.device.swipe(524, 351, 524, 1768)
            # self.device(resourceId="com.hawk.android.browser:id/refresh").click()
            self.device.delay(1)
            if self.device(resourceId=self.appconfig.id("id_progress", "Chrome")).wait.gone(timeout=30000):
                self.logger.debug("Website refresh " + str(loop + 1) + " times.")
            else:
                self.logger.debug("Website refresh " + str(loop + 1) + " times failed.")
                self.save_fail_img()
                self.chrome.exit()
                return False
        self.chrome.exit()
        return True

    def forget_first(self):
        self.open()
        if self.device(textStartsWith="Connected").wait.exists(timeout=5000):
            self.logger.debug("Disconnect wifi first!")
            self.device(textStartsWith="Connected").click()
            self.device(textContains='Forget').click.wait(timeout=2000)
        self.close()

    def open_close_wifi(self):
        '''open / close wifi
         argv: To see available networks -- closed 
               wifi list -- open
        '''
        self.logger.debug('Switch wifi')
        if self.close() and self.open():
            if self.device(textStartsWith="Connected").wait.exists(timeout=40000):
                self.logger.debug('wifi connect success!!!')
                self.device.delay(10)
                return True
            else:
                self.logger.debug('wifi connect fail!!!')
                self.save_fail_img()
                return False
        self.logger.debug('wifi switch fail!!!')
        self.save_fail_img()
        return False

    def enter_hotspot(self):
        self.logger.info("enter hot spot")
        self.enter_settings("Network & internet")
        hotsopt = self.device(text="Hotspot & tethering")
        assert hotsopt.wait.exists(), "******** can not find Network & Internet ********"
        hotsopt.click.wait(timeout=3000)
        self.device.delay(1)
        self.device(text="Mobile hotspot").click()

    def create_wifi_hotspot(self, ssid, password):
        self.logger.info("create %s wifi hotspot and open hotspot" % ssid)
        self.device(text="Set up mobile hotspot").click()
        self.device.delay(1)

        self.device(resourceId="com.android.settings:id/ssid").set_text(ssid)
        ssid = self.device(resourceId="com.android.settings:id/ssid").get_text()
        self.device(resourceId="com.android.settings:id/password").set_text(password)
        self.device(text="SAVE").click()
        self.device.delay(8)
        self.logger.info("open hotspot")
        # if not self.device(resourceId="com.android.settings:id/list").child(index=1).child(index=1). \
        #         child(checked=True, resourceId="android:id/switch_widget").wait.exists(timeout=5000):
        #     self.device(text="Mobile hotspot").click()

        self.click_text_ok()    # 如果hospot之前已经打开，需要多点击一下ok

        text = self.device(resourceId="android:id/switch_widget").get_text()
        if text == 'OFF':
            self.device(text="Mobile hotspot", resourceId="android:id/title").click()
            self.device.delay(1)
        self.click_text_ok()

        # hostpot_switcher = self.device(text="Mobile Hotspot").sibling(resourceId="android:id/switch_widget")
        # if hostpot_switcher.exists:
        #     self.logger.info(hostpot_switcher.get_text())
        # else:
        #     self.logger.info("can not find hostpot switcher")
        # if self.device(textContains="Not sharing").wait.exists(timeout=2000):
        #     self.device(textContains="Not sharing").click()

        if self.device(text="Mobile hotspot %s active" % ssid).wait.exists(timeout=10000):
            self.logger.info("create %s wifi hotspot and open hotspot success" % ssid)
            return ssid
        self.logger.info("create %s wifi hotspot and open hotspot failed" % ssid)
        self.save_fail_img()
        return False

    def close_hotspot(self):
        self.logger.info("close wifi hotspot")
        text = self.device(resourceId="android:id/switch_widget").get_text()
        if text == 'OFF':
            return True
        elif text == 'ON':
            self.device(text="Mobile hotspot", resourceId="android:id/title").click()
            self.device.delay(1)

        # verify
        text = self.device(resourceId="android:id/switch_widget").get_text()
        if text == 'OFF':
            return True
        self.logger.info("close wifi hotspot failed")
        self.save_fail_img()
        return False

    def connect_hotspot(self):
        self.logger.info("s-device connect wifi hotspot and browser web page")
        self.sdevice.open.quick_settings()
        self.sdevice(description="Wi-Fi").click.wait(timeout=2000)
        if self.sdevice(text="Always").wait.exists(timeout=2000):
            self.sdevice(text="Wi-Fi").click()
            self.sdevice(text="Always").clcik()
        self.device()


class Airplane(Settings):
    def enter(self):
        self.enter_settings("Network & internet")
        assert self.device(text="Airplane mode").ext5
        self.logger.debug("enter Airplane mode page successfully")

    def switch(self, status="OFF"):
        self.logger.debug('Switch airplane %s' % status)
        self.device.delay(1)
        # check = "false" if status == "OFF" else "true"
        if self.device(text="Airplane mode").right(resourceId='android:id/switch_widget').get_text() == status:
            self.logger.info("airplane status is %s" % status)
            return True
        else:
            self.device(text="Airplane mode").right(resourceId='android:id/switch_widget').click()
            self.device.delay(3)
            if self.device(text="Airplane mode").right(resourceId='android:id/switch_widget').get_text() == status:
                self.logger.info("Switch airplane %s success" % status)
                self.device.delay(2)
                return True
            self.logger.info("Switch airplane %s failed" % status)
            self.save_fail_img()
            return False


class Bt(Settings):
    def enter(self):
        # return self.enter_settings("Network & internet")
        return self.enter_settings("Bluetooth & device connection")
    def enter_bt(self):
        assert self.enter()
        bt = self.device(text="Bluetooth")
        assert bt.wait.exists(), "******** can not find Bluetooth item  ********"
        bt.click.wait(timeout=2000)

        return self.device(resourceId="com.android.settings:id/action_bar").child(text="Bluetooth").wait.exists()

    def switch(self, status="OFF"):
        self.logger.debug('Switch BT %s' % status)
        if self.device(text=status).exists:
            self.logger.info("BT status is %s" % status)
            return True
        else:
            bt_switcher = self.device(resourceId="com.android.settings:id/switch_widget")
            if not bt_switcher.wait.exists():
                bt_switcher = self.device(resourceId="com.android.settings:id/switchWidget")
            bt_switcher.click()
            if self.device(text=status).wait.exists(timeout=3000):
                self.logger.info("Switch BT %s success" % status)
                self.device.delay(5)
                return True
            self.logger.info("Switch BT %s failed" % status)
            self.save_fail_img()
            return False

    def enter_s(self):
        self.logger.info("s-device start bluetooth")
        self.sdevice.press.home()
        self.sdevice.delay()
        self.sdevice(text="Settings").click()
        self.sdevice.delay()
        if self.sdevice(text="Bluetooth").exists:
            self.sdevice(text="Bluetooth").click()
        else:
            self.sdevice(scrollable=True).scroll.vert.to(text="Bluetooth")
            if self.sdevice(text="Bluetooth").wait.exists(timeout=10000):
                self.sdevice(text="Bluetooth").click()
        if self.sdevice(text=self.appconfig("settings", "Settings")).wait.gone(timeout=2000):
            self.logger.info("s-device enter bluetooth")
            return True
        else:
            self.logger.info("s-device enter bluetooth failed")
            self.save_fail_img_s()
            return False

    def switch_s(self, status):
        self.logger.debug("s-device switch %s" % status)
        if self.sdevice(text=status).exists:
            self.logger.info("s-device location status is %s" % status)
            return True
        else:
            self.sdevice(resourceId="com.android.settings:id/switch_widget").click()
            if self.sdevice(text=status).wait.exists(timeout=3000):
                self.logger.info("s-device Switch BT %s success" % status)
                self.device.delay(2)
                return True
            self.logger.info("s-device Switch BT %s failed" % status)
            self.save_fail_img_s()
            return False

    def rename_bt_sdevice(self, sdevice_id):
        assert self.device(text="Device name").ext5
        self.device(text="Device name").click()

        assert self.device(text="Rename this device").ext5
        self.device(text="Rename this device").click()

        assert self.device(resourceId="com.android.settings:id/edittext").ext5
        self.device(resourceId="com.android.settings:id/edittext").set_text(sdevice_id)

        assert self.device(text="RENAME", enabled=True).ext5
        self.device(text="RENAME", enabled=True).click()

        self.logger.debug("Rename Sdevice BlueTooth successfully")
        return True

    def compare(self, sdevice_id):
        self.logger.info("m-device compare s-device")
        if self.device(text="Pair new device").wait.exists(timeout=3000):
            self.device(text="Pair new device").click()
        if self.device(text=sdevice_id).wait.exists(timeout=10000):
            self.logger.info("s-device bluetooth exists")
            self.device(text=sdevice_id).click()
            return True
        return False

    def cancel_compare(self):
        self.logger.info("m-device cancel compare s-device")
        self.device.delay()
        self.device(resourceId="com.android.settings:id/settings_button").click()
        self.device(text="FORGET").click()
        self.device.delay()
        if not self.device(resourceId="com.android.settings:id/settings_button").exists:
            self.logger.info("m-device cancel compare s-device success")
            return True
        else:
            self.logger.info("m-device cancel compare s-device failed")
            self.save_fail_img()
            return False

    def transfer(self, filename="Copy.rar"):
        self.logger.info("m-device transfer %s file to s-device" % filename)
        self.back_to_home()
        self.start_app("File manager")
        self.device(text="Phone").click()
        self.device(scrollable=True).scroll.vert.to(text=filename)
        self.device(text=filename).long_click()
        self.device(resourceId='com.jrdcom.filemanager:id/share_btn').click.wait(timeout=2000)
        self.device(text='Bluetooth').click.wait(timeout=2000)
        self.device(text='S-DEVICE').click.wait(timeout=2000)
        self.sdevice.open.notification()
        self.sdevice(text="Do you want to receive this file?").click.wait(timeout=2000)
        self.sdevice(text="Accept").click()
        self.sdevice.open.notification()
        self.device.open.notification()
        for i in range(5):
            self.device.delay(300000)
            if self.device(text="1 succeeded, 0 failed").exists and self.sdevice(
                    text="1 successful, 0 unsuccessful.").exists:
                self.logger.info("m-device transfer %s file to s-device success" % filename)
                self.sdevice(decription="Clear all notifications.").click()
                self.device(description="Clear all notifications.").click()
                self.back_to_home()
                return True
        self.logger.info("m-device transfer %s file to s-device failed" % filename)
        self.save_fail_img()
        self.back_to_home()
        return False


class GPS(Settings):
    def enter(self):
        try:
            assert self.enter_settings("Location"), "failed go to Location"
            # self.device(scrollable=True).scroll.vert.to(text="Location")
            # self.device(text="Location").click()
            assert self.device(resourceId="com.android.settings:id/action_bar").wait.exists() and self.device(text="Location").wait.exists()
        except:
            self.logger.warning(traceback.format_exc())
            self.save_fail_img()
        return True

    def switch(self, status="Off"):
        self.logger.debug('Switch gps %s' % status)
        if self.device(text=status).wait.exists(timeout=10000):
            self.logger.info("location status is already %s" % status)
            return True
        else:
            self.device(resourceId="com.android.settings:id/switch_widget").click()
            self.device.delay(5)
            if self.device(text=status).wait.exists(timeout=10000):
                self.logger.info("Switch gps %s success" % status)
                self.device.delay(2)
                return True
            self.logger.info("Switch gps %s failed" % status)
            self.save_fail_img()
            return False


class NFC(Settings):
    def enter(self):
        self.enter_settings("Bluetooth & device connection")
        # verify
        # assert self.device(text="NFC").wait.exists()
        if self.device(text="NFC").exists:
            return True
        else:
            return False

    def switch(self, status="OFF"):
        self.logger.debug('Switch NFC to %s' % status)
        optional_text = ["OFF", "ON"]
        # get status
        text = self.device(resourceId="android:id/switch_widget").get_text()
        # self.logger.info("before click icon, get status: " + text)
        # self.device.delay(5)
        if text in optional_text and text == status:
            self.logger.info("NFC status is %s" % text)
            return True
        else:
            self.device(resourceId="android:id/switch_widget").click()
            self.device.delay(2)
            text = self.device(resourceId="android:id/switch_widget").get_text()
            if text == status:
                self.logger.info("Switch NFC %s success" % status)
                return True

        self.logger.info("Switch NFC %s failed, because get status: %s" % (status, text))
        self.save_fail_img()
        return False


class DualSim(Settings):

    def __init__(self, device, log_name, sdevice=None):
        Settings.__init__(self, device, log_name, sdevice)
        self.unicom_str = 'China Unicom '

    def _enter_network_internet(self):
        assert self.enter_settings("Network & internet"), "enter Network & internet failed"

    def enter_sim(self):
        self._enter_network_internet()

        cellular_network = self.device(text="Cellular network")
        assert cellular_network.wait.exists(), "******** can not find Cellular network  ********"
        cellular_network.click.wait(timeout=3000)

    def _enter_sim_manager(self):
        self._enter_network_internet()

        sim_manger = self.device(text="SIM cards")
        assert sim_manger.wait.exists(), "******** SIM cards ********"
        sim_manger.click.wait(timeout=3000)

        # verify
        assert self.device(text="PREFERRED SIM FOR").wait.exists(), "******** PREFERRED SIM FOR not found  ********"

    def switch_sim(self, sim_card=1, switch="ON"):
        """sim_card 1,2
           switch  OFF ON
        """
        self.logger.info("switch sim card %d to %s" % (sim_card, switch))
        if switch == "OFF":
            if self.device(text="SIM %d is Disabled" % sim_card).wait.exists(timeout=2000):
                self.logger.info("sim card %d is OFF" % sim_card)
                return True
            self.device(index=sim_card, className="android.widget.LinearLayout").child(index=2).click()
            self.device(text="OK").click()
            self.device(text="OK").click.wait(timeout=5000)
            if self.device(text="SIM %d is Disabled" % sim_card).wait.exists(timeout=2000):
                self.logger.info("sim card %d switch to OFF success" % sim_card)
                return True
            self.logger.info("sim card %d switch to OFF failed" % sim_card)
            self.save_fail_img()
            return False
        else:
            if not self.device(text="SIM %d is Disabled" % sim_card).wait.exists(timeout=2000):
                self.logger.info("sim card %d is ON" % sim_card)
                return True
            self.device(index=sim_card, className="android.widget.LinearLayout").child(index=2).click()
            self.device(text="OK").click.wait(timeout=5000)
            if not self.device(text="SIM %d is Disabled" % sim_card).wait.exists(timeout=2000):
                self.logger.info("sim card %d switch ON success" % sim_card)
                return True
            self.logger.info("sim card %d switch ON failed" % sim_card)
            self.save_fail_img()
            return False

    def switch_sim_new(self, sim):
        """
        switch sim to target network type in duel sim mode
        :param net_type: 2G, 3G, 4G
        :param sim: 1 or 2 only
        :return:
        """
        try:
            self.logger.info("switch sim card %d" % sim)
            sim_str = '{}{}'.format(self.unicom_str, sim)
            self.device(text=sim_str).click()
            self.device.delay(1)
            return True
        except:
            return False

        # select sim
        # tab_res = self.device(resourceId="android:id/tabs")
        # assert tab_res.wait.exists(), "******** can not find android:id/tabs ********"
        # tab_res.child(className="android.widget.LinearLayout", index=sim - 1).click()
        #
        # # verify
        # return tab_res.child(className="android.widget.LinearLayout", index=sim - 1, selected=True).wait.exists()

    def select_preferred_net_type(self, net_type, sim=1):
        self.logger.info("try to select %s" % net_type)
        type_temp = "4G" if net_type == "LTE" else net_type

        if self.device(text="Cellular networks").wait.exists(timeout=2000):
            self.device(text="Cellular networks").click()

        if self.device(text="Advanced").wait.exists(timeout=2000):
            self.device(text="Advanced").click()

        preferred_net = self.device(text="Preferred network type")
        assert preferred_net.wait.exists(), "******** can not find Preferred network type  ********"
        preferred_net.click.wait(timeout=3000)

        target_net = self.device(textStartsWith=type_temp, className="android.widget.CheckedTextView")
        assert target_net.wait.exists(), "******** can not find %s ********" % net_type
        target_net.click.wait(timeout=3000)

        self.device.delay(10)
        return self._is_connected(net_type, sim)

    def switch_data_new(self, sim_card=1, switch='ON'):
        self.logger.info("switch sim card data %d to %s" % (sim_card, switch))
        root = self.device(resourceId="com.android.settings:id/recycler_view")
        sim1 = root.child(className="android.widget.RelativeLayout", index=5)
        sim2 = root.child(className="android.widget.RelativeLayout", index=9)
        sim_dict = {1: sim1, 2: sim2}
        status = sim_dict.get(sim_card).child(resourceId="android:id/switch_widget",
                                              className="android.widget.Switch").get_text()
        if switch == status:
            self.logger.info("mobile data is %s" % status)
            return True

        sim_dict.get(sim_card).click()
        if self.device(text="Change data SIM?").wait.exists(timeout=2000):
            self.device(text="OK").click()
            self.device.delay()

        # verify
        status = sim_dict.get(sim_card).child(resourceId="android:id/switch_widget").get_text()
        if switch == status:
            self.logger.info("mobile data is %s" % status)
            return True

        self.logger.error("******* data switch failed ******")
        return False

        # action_dict = {'ON': '- %d' % sim_card, 'OFF': 'Turn off cellular data'}
        #
        # status = 'ON'
        # if self.device(text="Turn off mobile data").wait.exists(timeout=3000):
        #     status = 'OFF'
        #
        # cellular_data = self.device(text="Cellular data")
        # if switch == status:
        #     self.logger.info("mobile data is %s" % status)
        #     return True
        # else:
        #     cellular_data.click.wait()
        #     self.device(textContains=action_dict[switch]).click()
        #
        # self.device.delay(5)
        #
        # # verify
        # status = 'ON'
        # if self.device(text="Turn off mobile data").wait.exists(timeout=3000):
        #     status = 'OFF'
        # self.logger.info("to switch=%s, status=%s done" % (switch, status))
        # if status == switch:
        #     return True
        #
        # return False

    def switch_data(self, sim_card=1, switch="ON"):
        self.logger.info("switch sim card data %d to %s" % (sim_card, switch))
        self.device(scrollable=True).scroll.vert.toBeginning(steps=100, max_swipes=100)
        if sim_card == 2:
            self.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)

        status = self.device(resourceId="android:id/switch_widget").get_text()
        if switch == status:
            self.logger.info("Cellular data is %s" % status)
            return True
        else:
            self.device(resourceId="android:id/switch_widget").click()
            switch_data = self.device(text="Turn off cellular data?")
            if switch_data.wait.exists():
                self.device(text="OK").click()
            self.device.delay()
            status = self.device(resourceId="android:id/switch_widget").get_text()
            return status == switch

        # self.device(scrollable=True).scroll.vert.to(text="Mobile (SIM2)")
        # self.device.swipe(93, 1082, 93, 370, 100)
        # if self.device(resouceId="android:id/list").child(index=1).child(index=0).child(text=switch).wait.exists(
        #         timeout=2000):
        #     self.logger.info("sim card data %d is %s" % (sim_card, switch))
        #     return True
        # self.device(resouceId="android:id/list").child(index=1).child(index=0).child(index=1).click()
        # if self.device(resouceId="android:id/list").child(index=1).child(index=0).child(text=switch).wait.exists(
        #         timeout=2000):
        #     self.logger.info("switch sim card data %d to %s success" % (sim_card, switch))
        #     return True
        # self.logger.info("switch sim card data %d to %s failed" % (sim_card, switch))
        # self.save_fail_img()
        # return False

    def enter_data(self, sim_card=1):
        self._enter_network_internet()
        self.device(text="Data usage").click()
        # return self.enter_settings("Data usage")
        # self.device(resouceId="android:id/tabs").child(index=sim_card - 1).click()

    def select_preferred_sim(self, sim, action):
        """

        :param sim:
        :param action: data/call/msg
        :return:
        """
        self.logger.info("select preferred action %s for sim %s " % (action, sim))
        if action == "data":
            wrapped_ac = "Cellular data"
        elif action == "call":
            wrapped_ac = "Calls"
        elif action == "msg":
            wrapped_ac = "SMS messages"
        else:
            return False

        self._enter_sim_manager()
        self.device(text=wrapped_ac).click()

        assert self.device(resourceId="com.tct:id/tct_dialog_list_view").wait.exists(), "**** do not get popup panel ****"
        sim_content = "中国联通 %s" % sim
        self.device(text=sim_content).click()

        # verify
        text = self.device(text=wrapped_ac).sibling(resourceId="android:id/summary").get_text()
        self.logger.warning("text:%s" % text)
        if str(text) == str(sim_content):
            self.logger.info("select preferred action %s for sim %s pass" % (action, sim))
            return True
        self.logger.error("******* select %s to %s fail ******" % (sim, action))
        return False

        # content = self.device(resourceId="android:id/list")
        # child_count = content.info["childCount"]
        # print child_count
        # for i in range(child_count):
        #     if content.child(className="android.widget.LinearLayout", index=i).child(text=wrapped_ac).exists:
        #         atext = content.child(className="android.widget.LinearLayout", index=i).child(index=1).get_text()
        #         if "- %s" % sim in atext:
        #             self.logger.info("select preferred action %s for sim %s pass" % (action, sim))
        #             return True
        # self.logger.error("******* select %s to %s fail ******" % (sim, action))
        # return False


class GoogleReq(Settings):
    def verify_play_store(self):
        self.logger.info("checking play store")
        if self.device(text="Play Store").wait.exists():
            return True
        else:
            self.logger.error("******* can not find play store ******")
            return False

    def verify_Google_search(self):
        self.logger.info("checking Google search")
        if self.device(packageName="com.google.android.googlequicksearchbox").wait.exists():
            return True
        else:
            self.logger.error("******* can not find Google search widget ******")
            return False

    def verify_default_search(self):
        self.logger.info("checking Google search")
        self.device.press.home()
        self.device(resourceId="com.google.android.googlequicksearchbox:id/search_plate").click()
        self.device(resourceId="com.google.android.googlequicksearchbox:id/search_box").set_text("google")
        self.device.press.enter()
        if self.device(resourceId="com.google.android.googlequicksearchbox:id/logo_header_logo_view",
                       packageName="com.google.android.googlequicksearchbox").wait.exists(timeout=10000):
            status = True
        else:
            status = False
        screen = self.save_fail_img_adv()
        return status, screen

    def verify_google_folder(self):
        """
        check Google folder, the folder MUST be named Google,
        and the order of core app must be:Google, Chrome, Gmail, Maps, YouTube, Drive, Play Music, Duo, Photos
        :return:
        """
        self.logger.info("checking Google folder")
        expect_app_list_in_folder = ['Google', 'Chrome', 'Gmail', 'Maps', 'YouTube', 'Drive', 'Play Music',
                                     'Play Movies & TV', 'Duo', 'Photos']

        # assert Google folder exist
        ret, screen = self._open_google_folder()
        if not ret:
            return 'FAIL', screen

        # assert the folder is opened
        assert self.device(
            resourceId="com.blackberry.blackberrylauncher:id/panel_grid_view").wait.exists(), "******** can not open the Google folder ********"

        # get app list in Google folder
        current_app_list_in_folder = self._get_app_list_from_folder()

        # check the order
        self.logger.info("checking the app order")
        for expect, current in zip(expect_app_list_in_folder, current_app_list_in_folder):
            assert expect == current, "expect app is %s, but %s found" % (expect, current)
        else:
            self.logger.info("current app order is OK")

        # verify all apps are Google ones or not
        self._verify_app_package_name()
        return 'PASS', screen

    def _open_google_folder(self):
        google_folder = self.device(resourceId="com.blackberry.blackberrylauncher:id/title", text="Google")
        screen = self.save_fail_img_adv()
        if not google_folder.wait.exists():
            self.logger.error("******** can't find Google folder  ********")
            return False, screen
        # assert google_folder.wait.exists(), "******** can't find Google folder  ********"
        google_folder.click.wait()
        screen = self.save_fail_img_adv()
        return True, screen

    def _get_app_list_from_folder(self):
        """
        get app list from folder, iterate the index, break if get exception(ui can not be found).
        :return:
        """
        current_app_list_in_folder = []
        folder_panel = self.device(resourceId="com.blackberry.blackberrylauncher:id/panel_grid_view")
        index = 0
        while True:
            try:
                app_name = folder_panel.child(index=index).child(index=0).get_text()
                print index, app_name
                current_app_list_in_folder.append(app_name)
                index += 1
            except:  # ui not found exception
                self.logger.info("got exception, iterate folder done")
                # self.logger.warning(traceback.format_exc())
                break
        return current_app_list_in_folder

    def _verify_app_package_name(self):
        """
        verify the current activity has the give keyword
        :param keyword:
        :return:
        """
        allow_app_list = ["com.google.android.configupdater",
                          "com.google.android.gms",
                          "com.google.android.backuptransport",
                          "com.google.android.feedback",
                          "com.google.android.gsf.login",
                          "com.google.android.onetimeinitializer",
                          "com.google.android.partnersetup",
                          "com.google.android.gsf",
                          "com.android.vending",
                          "com.google.android.setupwizard",
                          "com.google.android.googlequicksearchbox",
                          "com.google.android.tag",
                          "com.google.android.ext.services",
                          "com.google.android.packageinstaller",
                          "com.google.android.maps",
                          "com.google.android.media.effects",
                          "com.android.chrome",
                          "com.google.android.apps.docs",
                          "com.google.android.apps.tachyon",
                          "com.google.android.gm",
                          "com.google.android.syncadapters.calendar",
                          "com.google.android.syncadapters.contacts",
                          "com.google.android.talk",
                          "com.google.android.apps.maps",
                          "com.google.android.music",
                          "com.google.android.apps.photos",
                          "com.google.android.videos",
                          "com.google.android.webview",
                          "com.google.android.youtube",
                          "com.google.android.tts",
                          "com.google.android.apps.walletnfcrel",
                          "com.google.android.apps.books",
                          "com.google.android.calculator",
                          "com.google.android.calendar",
                          "com.google.android.apps.cloudprint",
                          "com.google.android.deskclock",
                          "com.google.android.apps.enterprise.dmagent",
                          "com.google.android.apps.docs.editors.docs",
                          "com.google.android.apps.docs.editors.sheets",
                          "com.google.android.apps.docs.editors.slides",
                          "com.android.facelock",
                          "com.google.android.apps.inputmethod.hindi",
                          "com.google.android.inputmethod.pinyin",
                          "com.google.android.inputmethod.japanese",
                          "com.google.android.keep",
                          "com.google.android.inputmethod.korean",
                          "com.google.android.inputmethod.latin",
                          "com.google.android.play.games",
                          "com.google.android.apps.plus",
                          "com.google.android.marvin.talkback",
                          "com.google.android.apps.magazines",
                          "com.google.android.apps.genie.geniewidget",
                          "com.google.android.apps.messaging",
                          "com.google.android.ext.shared",
                          "com.google.android.printservice.recommendation"]
        self.logger.info("verify app package name in Google folder")

        # assert the folder is opened
        assert self.device(
            resourceId="com.blackberry.blackberrylauncher:id/panel_grid_view").wait.exists(), "******** can not open the Google folder ********"

        # iterate app list, launch the app one by one, and verify the package name
        folder_panel = self.device(resourceId="com.blackberry.blackberrylauncher:id/panel_grid_view")
        index = 0
        while True:
            try:
                app = folder_panel.child(index=index).child(index=0)
                app_name = app.get_text()
                app.click.wait()
                self.device.delay()
                current_package = self.device.info["currentPackageName"]
                self.logger.info("start %s_%s, *%s* in white list" % (index, app_name, current_package))
                assert current_package in allow_app_list, "***** this package name *%s* is not in white list" % current_package
                self.logger.info("%s is in white list" % current_package)
                self.device.delay()
                self.device.press.home()
                self._open_google_folder()
                self.device.delay(1)
                index += 1
            except:  # ui not found exception
                self.logger.info("got exception, iterate folder done")
                # self.logger.warning(traceback.format_exc())
                break

    def check_su_process(self):
        """
        check su process
        :return:
        """
        self.logger.info("checking su process")
        return not self.adb.is_kw_in_shell_output(cmd="ls system/xbin", keywords="su")

    def check_backup_transport(self):
        """
        check backup transport config
        :return:
        """
        self.logger.info("checking backup transport")
        return self.adb.is_kw_in_shell_output(cmd="bmgr list transports",
                                              keywords="* com.google.android.gms/.backup.BackupTransportService")

    def check_ru_feature_string(self):
        """
        Run adb shell pm list features
        Verify the following line is present com.google.android.feature.RU
        :return:
        """
        self.logger.info("checking feature: com.google.android.feature.RU")
        return self.adb.is_kw_in_shell_output(cmd="pm list features", keywords="com.google.android.feature.RU")

    def check_vendor_build_fingerprint(self):
        """
        get return adb shell getprop ro.vendor.build.fingerprint
        :return:
        """
        self.logger.info("checking property: ro.vendor.build.fingerprint")
        return self.adb.is_kw_in_shell_output(cmd="getprop ro.vendor.build.fingerprint",
                                              keywords="ro.vendor.build.fingerprint")

    def check_safe_mode(self):
        """
        safe mode
        :return:
        """
        # long press power,
        self.logger.info("checking safe mode")
        self.adb.LongPressPower()

        # then lang press power off,
        assert self.device(
            text="Power off").wait.exists(), "******** can not find power off after long press power key ********"
        self.device(text="Power off").long_click()
        self.device(text="Power off").wait.gone(timeout=3000)

        self.device.delay(1)
        screen = self.save_fail_img_adv()

        # check the safe mode layout
        assert self.device(
            text="Reboot to safe mode").wait.exists(), "******** can not find safe mode after long press power off  ********"

        self.back_to_home()
        assert self.device(
            resourceId="com.blackberry.blackberrylauncher:id/icon_background").wait.exists(), "******** can not return to home  ********"

        return 'PASS', screen

    def verify_verify_apps(self):
        """
        verify apps
        :return: 
        """
        self.logger.info("checking settings->verify apps")
        self.back_to_home()

        # login Google account
        self.login_google_account()

        # verify settings
        return self.enter_verify_settings()

    def enter_verify_settings(self):
        self.back_to_home()

        # go to verify apps settings
        self.enter_settings("Google")

        self.device(scrollable=True).scroll.vert.to(text="Security")
        assert self.device(text="Security").wait.exists(), "******** can not find security btn  ********"
        self.device(text="Security").click.wait(timeout=3000)

        # menu changed from 'Verify Apps' to 'Google Play Protect'
        assert self.device(
            text="Google Play Protect").wait.exists(), "******** can not find Google Play Protect  ********"
        self.device(text="Google Play Protect").click.wait(timeout=3000)

        assert self.device(
            text="Scan device for security threats").wait.exists(), "******** can not find 'Scan device for security threats'  ********"
        assert "ON" in self.device(
            resourceId="com.google.android.gms:id/toggle").get_text(), "******** 'Scan device for security threats' is OFF"
        return True

    def check_test_app_in_apps(self):
        """
        iterate settings->apps
        get app name
        :return: a set include test keyword in app name
        """
        self.logger.info("checking test app in apps")
        self.back_to_home()

        # go to apps settings

        self.enter_settings("Apps & notifications")
        self.device.delay(1)
        self.device(scrollable=True).scroll.vert.toEnd(steps=100, max_swipes=100)

        see_all_apps = self.device(textStartsWith="See all")
        assert see_all_apps.wait.exists(), "**** can not find See all xx apps option ****"
        see_all_apps.click.wait(timeout=3000)

        self.device.delay(3)  # wait all apps loading
        app_list = []

        while True:
            first_app = self.device(resourceId="android:id/title").get_text()
            app_num = self.device(resourceId="android:id/icon").count
            for i in range(app_num):
                try:
                    app_title = self.device(resourceId="android:id/list").child(index=i).child(index=0).child(
                        resourceId="android:id/title").get_text()
                except:
                    app_title = ""
                    self.logger.debug("skip")
                app_list.append(app_title)
                self.device.wait("idle")

            self.device(resourceId="android:id/list", scrollable=True).scroll.vert.forward()
            if self.device(resourceId="android:id/title").get_text() == first_app:
                break

        app_list = list(set(app_list))
        return app_list
        # show system apps - no need show the system one, they have no icon to start
        # assert self.device(description="More options").wait.exists(), "******** can not find menu btn ********"
        # self.device(description="More options").click.wait(timeout=3000)
        # assert self.device(text="Show system").wait.exists(), "******** can not find show system btn  ********"
        # self.device(text="Show system").click.wait(timeout=3000)
        # self.device.delay()  # wait all apps re-load

        # top_x, top_y = self.device(resourceId="android:id/list").get_top_location
        # bottom_x, bottom_y = self.device(resourceId="android:id/list").get_bottom_location()
        # print "top(%s,%s), bottom(%s,%s)" % (top_x, top_y, bottom_x, bottom_y)

        # get ui location
        # info = self.device(resourceId="android:id/list").info
        # top, left = info["bounds"]["top"], info["bounds"]["left"]
        # cild_count = info["childCount"] - 1  # Mercury 显示不全，数量-1
        #
        # item_info = self.device(resourceId="android:id/list").child(index=0).info
        # item_bottom = item_info["bounds"]["bottom"]
        # item_height = item_bottom - top
        #
        #
        # sx = left+1  # swipe start x
        # sy = item_height*cild_count + top  # swipe start y
        # is_bottom_end = False
        # print item_height, sx, sy, cild_count
        #
        # # iterate app list, add them in a set,
        # apps_set = set("")
        # last_app = ""
        # while True:
        #     try:
        #         loops = cild_count if not is_bottom_end else cild_count+2
        #         for i in range(loops):
        #             last_app = self.device(resourceId="android:id/list").child(index=i).child(resourceId="android:id/title").get_text()
        #             print last_app
        #             apps_set.add(last_app)
        #         else:
        #             self.device.swipe(sx, sy, sx, top, steps=100)
        #             if self.device(text=last_app).wait.exists(timeout=1):
        #                 is_bottom_end = True
        #     except:
        #         break
        #
        # # verify the set simply
        # assert "Updates" in apps_set, "can not find Updates in the app list iterated from device"
        # assert len(apps_set) > 40
        #
        # # to lower case
        # apps_list = set(item.lower() for item in apps_set)
        # # print apps_list
        #
        # #check test in app name
        # appname_with_test = set(item for item in apps_list if "test" in item)
        # # print appname_with_test
        #
        # # return test apps list
        # return appname_with_test


if __name__ == '__main__':
    a = Wifi("14698686", "Wifi")
    # print a.get_current_screen_lock()

    # a = DualSim("3dc2a8f3", "DualSim")
    # a.switch_network_for_multi_menus('2G')
    a.close_hotspot()