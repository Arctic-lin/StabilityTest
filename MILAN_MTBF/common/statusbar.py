# -*- coding: UTF-8 -*-
from common import *


class StatusBar(Common):

    def switch_icon(self, status, icon_instance, icon_name):
        self.logger.info("switch {} to {}".format(icon_name, status))
        self.device.delay(1)
        # self.device(scrollable=True).scroll.horiz.to(descriptionStartsWith=icon_name)
        self.device.delay(1)
        text = icon_instance.get_text()
        # 与预期相同，直接返回
        if status == text:
            self.logger.info("{} status is {} already".format(icon_name, status))
            return True
        self.device.delay()
        # 与预期不同，点击进行状态切换
        if icon_name=="Bluetooth":
            #点击Bluetooth图标
            self._click_and_log("Bluetooth in QuickSettings",623, 260)
        else:
            icon_instance.click()
        self.device.delay(2)
        text = icon_instance.get_text()

        self.device.delay(5)

        # verify
        if status == text:
            self.logger.info("switch {} to {} success".format(icon_name, status))
            return True
        else:
            self.logger.info("switch {} to {} fail".format(icon_name, status))
            self.save_fail_img()
            return False



    def switch_hospot(self, status):
        self.device.delay ()
        ret = self.switch_icon(status, self.device(descriptionStartsWith="Hotspot"), 'Hotspot')
        return ret

    def switch_airplane(self, status):
        self.device.delay()
        ret = self.switch_icon(status, self.device(descriptionStartsWith="Airplane"), 'Airplane')
        return ret

    def switch_gps(self, status):
        """OFF ON
        """
        self.device.delay ()
        ret = self.switch_icon(status, self.device(descriptionStartsWith="Location"), 'Location')
        return ret

    def switch_nfc(self, status):
        """OFF ON
        """
        self.device.delay ()
        ret = self.switch_icon(status, self.device(description="NFC"), 'NFC')
        return ret

    def switch_bt(self, status):
        self.device.delay ()
        ret = self.switch_icon(status, self.device(descriptionStartsWith="Bluetooth"), 'Bluetooth')
        return ret

    def switch_wifi(self):
        self.device.delay ()
        self.logger.debug('Switch wifi')
        wifi_switcher = self.device(resourceId="com.android.systemui:id/quick_settings_panel").child(index=2).child(
            index=0)
        if self.device(description='Wi-Fi is off.'):
            wifi_switcher.click()
            if self.device(description='Wi-Fi is off.').wait.gone(timeout=10000):
                self.logger.debug('wifi is opened!')
                return True
            else:
                self.logger.debug('wifi open fail!!!')
                return False
        else:
            wifi_switcher.click()
            if self.device(description='Wi-Fi is off.').wait.exists(timeout=10000):
                self.logger.debug('wifi is closed!')
                return True
            else:
                self.logger.debug('wifi close fail!!!')
                return False



