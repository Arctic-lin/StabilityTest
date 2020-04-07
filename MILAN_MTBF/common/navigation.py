# -*- coding: UTF-8 -*-
"""Telephony library for scripts.
"""
from common import *


class MenuNavigation(Common):

    def _apps_navigation(self):
        self.logger.info("start 16 apps from navigation interface")
        self.clear_background()
        self.device.press.home()
        self.enter_main_apps()

        icons = self.device(resourceId="com.tcl.android.launcher:id/icon").count
        print icons
        for i in range(4, 21):
            text = self.device(resourceId="com.tcl.android.launcher:id/apps_list_view").child(resourceId="com.tcl.android.launcher:id/icon", index=i).get_text()
            if self.is_in_ignore_list(text):
                continue
            self.device(resourceId="com.tcl.android.launcher:id/apps_list_view").child(resourceId="com.tcl.android.launcher:id/icon", index=i).click.wait()

            el = self.device(resourceId='com.tcl.android.launcher:id/search_box_input')
            self.allow_permissions()
            if el.wait.gone(timeout=5000):
                self.logger.info("start %dth app success" % (i + 1))
            else:
                self.logger.info("start %dth app failed" % (i + 1))
                self.save_fail_img()
                return False
            self.back_to_mainapps()

        # el = self.device(description='Apps')
        # el.click()
        # self.device.delay(4)
        # self.device().scroll.vert.toBeginning()
        # self.device.press.home()
        # self.device.delay(4)
        # for i in range(16):
        #     self.device(description="Apps").click()
        #     self.device.delay(4)
        #     apps = self.device(resourceId='com.tcl.android.launcher:id/apps_list_view')
        #     app = apps.child(resourceId='com.tcl.android.launcher:id/icon', index=(i + 1))
        #     app.click.wait(timeout=20000)
        #     self.device.delay(2)
        #     el = self.device(resourceId='com.tcl.android.launcher:id/search_button')
        #     if el.wait.gone(timeout=5000):
        #         self.logger.info("start %dth app success" % (i + 1))
        #     else:
        #         self.logger.info("start %dth app failed" % (i + 1))
        #         self.save_fail_img()
        #         return False
        #     self.device.press.home()
        #     self.device.delay()
        #     self.device.press.home()
        self.logger.info("start 16 apps from navigation interface success")
        return True

    def back_to_mainapps(self):
        el = self.device(resourceId='com.tcl.android.launcher:id/search_box_input')
        for i in range(5):
            if el.wait.exists():
                break
            else:
                self.device.press.back()
                self.device.delay(1)
        else:
            self.device.press.home()
            self.enter_main_apps()

    def _launcher_navigation(self):
        self.logger.info("start apps from launcher interface")
        self.device.press.home()

        content = self.device(resourceId='com.tcl.android.launcher:id/workspace')
        icon_count = self.device(className='android.widget.TextView').count
        started_app_count = 0

        if not icon_count:
            self.logger.error("******* have no icon to start, or script issue ******")
            return False

        self.logger.debug("home page icon_count:%d"%icon_count)
        for i in range(icon_count):
            expect_child = content.child(index=i, className='android.widget.TextView')
            if not expect_child.exists:  # maybe have no app started if id changed, but this case will be always pass
                continue

            expect_child_desc = expect_child.info["contentDescription"]  # if a widget do not loaded
            if not expect_child_desc:
                continue

            icon_text = expect_child.get_text()
            if icon_text is None or self.is_in_ignore_list(icon_text):
                continue

            self.start_app(icon_text, b_desk=True)
            self.device.delay(4)
            if not self.device(resourceId='com.tcl.android.launcher:id/workspace').exists:
                started_app_count += 1
                self.logger.info("start app-%s success" % icon_text)
            else:
                self.logger.info("start app-%s failed" % icon_text)
                self.save_fail_img()
                return False
            self.device.press.home()
            self.device.delay(2)

        # verify
        self.device.press.home()
        if started_app_count > 0:
            self.logger.info("start %s apps from launcher interface success" % started_app_count)
            return True
        else:
            self.logger.error("have no started app, check your script^_^")
            return False

    def is_in_ignore_list(self, content):
        # some app should ignore, it maybe block test process
        # WD add lock
        white_list = ['Getting started', 'Google', 'Duo', 'Smart Manager', 'Alcatel Demo Assistant', 'Compass', 'Lock', 'User Support']
        return content in white_list


if __name__ == '__main__':
    a = MenuNavigation("3dc2a8f3", "MenuNavigation")
    # a.device(resourceId="com.tct.launcher:id/icon", index=6).click()
    # a.start_app("Hangouts", b_desk=False)
    a._apps_navigation()
    # print a.device.dump()
