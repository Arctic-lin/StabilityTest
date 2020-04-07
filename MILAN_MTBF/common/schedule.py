# -*- coding: utf-8 -*-

import re
from common import *
from random_utils import random_name
from ui_parser import UIParser


class Schedule(Common):
    """Provide common functions involved Calendar."""
    def __init__(self, device, log_name, sdevice=None):
        Common.__init__(self, device, log_name, sdevice=None)
        self.create_event_btn = self.device(resourceId="com.google.android.calendar:id/floating_action_button")
        self.set_today_btn = self.device(resourceId="com.google.android.calendar:id/action_today")
        self.alarm_item = self.device(resourceId="com.android.deskclock:id/digital_clock")
        self.add_new_btn = self.device(resourceId="com.android.deskclock:id/fab")

    def enter_calendar(self):
        '''Launch calender by start activity.
        '''

        if self.is_calendar_home():
            self.logger.info('calendar already opened')
            return True
        self.start_app("Calendar")

        self.skip_intro()
        self.allow_steps()
        self.dismiss_sync()
        # self.select_Agenda()
        return self.is_calendar_home()

    def is_calendar_home(self):
        if self.create_event_btn.wait.exists():
            return True
        return False

    def select_Agenda(self):
        try:
            assert self.device(description="Show Calendar List and Settings drawer").wait.exists(timeout=3000)
            self.device(description="Show Calendar List and Settings drawer").click()

            assert self.device(text="Agenda").ext5
            self.device(text="Agenda").click()

            # assert self.device(resourceId="com.blackberry.calendar:id/agenda_month_name").ext5
            self.logger.debug("select Agenda successfully")
            return True
        except:
            self.logger.warning("select Agenda failed")
            self.save_fail_img()
            self.logger.warning(traceback.format_exc())

    def enter_and_dismiss_if_need(self):

        self.logger.debug("Launch calendar dismiss welcome screen if needed.")
        if self.enter_calendar():
            return True
        if self.device(text="BlackBerry Calendar").wait.exists():
            assert self.device(
                resourceId="com.blackberry.calendar:id/introductory_slide_skip_button").wait.exists(), "******** can not find skip btn ********"
            self.device(resourceId="com.blackberry.calendar:id/introductory_slide_skip_button").click()
            self.device(resourceId="com.blackberry.calendar:id/introductory_slide_skip_button").wait.gone(timeout=3000)

        return self.device(resourceId="com.blackberry.calendar:id/create_event_fan_root_fab").wait.exists(timeout=3000)

    def create_calendar(self, name):
        self.logger.debug('create a new event %s' % name)
        self.set_today_btn.click()
        self.set_today_btn.click()
        self.device.wait.idle()

        # create event
        self.create_event_btn.click()
        self.device.wait.idle()
        if self.device(description="Event button").exists:
            self.device(description="Event button").click()
        self.device.wait.idle()

        # input title
        self.logger.debug('input event %s' % name)
        titles = [self.device(resourceId="com.google.android.calendar:id/title"),
                  self.device(resourceId="com.google.android.calendar:id/title_edit_text")]
        for title in titles:
            if title.wait.exists(timeout=2000):
                title.set_text(name)
                self.device.wait.idle()
                break
        else:
            self.logger.debug('can not find title id')
            return False

        # more options
        if self.device(text="More options").wait.exists(timeout=2000):
            self.device(text="More options").click()
            self.device.wait.idle()

        # All day
        self.device(text="All-day").click()
        self.device.wait.idle()

        # swipe to top
        sx, sy, ex, ey = 790, 1384, 790, 310
        self.device.swipe(sx, sy, ex, ey, steps=100)
        self.device.delay(1)

        # add location
        self.device(text="Add location").click()
        self.device.wait.idle()

        self.logger.debug('input event %s location' % name + "_location")
        self.device(text="Add location").set_text(name + "_location")
        self.device.press.enter()
        self.device.wait.idle()

        # save
        self.click_save_btn()
        self.device.wait.idle()
        if self.device(text="Set default calendar").exists:
            self.device(text="YES").click()
            self.device.delay(1)

        # verify
        return self._verify_calendar_creation(name)

    def _verify_calendar_creation(self, name):
        self.logger.info('verify calendar creation')
        for i in range(10):
            self.set_today_btn.click()
            self.device.delay(timeout=2)
            if self.device(descriptionContains=name).wait.exists(timeout=20000):
                self.logger.info('create a new event %s success' % name)
                return True
            else:
                for i in range(10):
                    self.device.swipe(100, 1400, 100, 500, steps=100)
                    if self.device(text=name).wait.exists(timeout=1000):
                        return True

        self.logger.debug("create calendar failed")
        self.save_fail_img()
        if self.device(text="Discard").wait.exists(timeout=1000):
            self.device(text="Discard").click()
        return False

    def delete_calendar(self, name, selcetor='text'):
        self.logger.info("delete the %s events" % name)

        if self.device(descriptionContains=name).wait.exists(timeout=3000):
            self.device(descriptionContains=name).click()
            self.device.wait.idle()
            if self.device(description="More options").wait.exists(timeout=3000):
                self.device(description="More options").click()
            self.device.wait.idle()
            if self.device (text="Delete").wait.exists(timeout=3000):
                self.device(text="Delete").click()
            self.device.wait.idle()
            self.device(text="Delete", resourceId="android:id/button1").click()
            self.device.wait.idle()
        else:
            self.logger.error("******* can not find event:{} ******".format(name))
            return False

        # verify
        if not self.device(descriptionContains=name).exists:
            self.logger.info("delete the %s events success" % name)
            return True
        else:
            self.logger.info("delete the %s events failed" % name)
            self.save_fail_img()
            return False

    def delete_calendar_all(self):
        try:
            self.enter_calendar()
            self.logger.info("start delete all the events")
            # event_title = self.device(textStartsWith="Auto", resourceId="com.blackberry.calendar:id/title")
            event_title = self.device(resourceId="com.blackberry.calendar:id/agenda_instance_tile_title")

            for i in range(30):
                if event_title.wait.exists(timeout=2000):
                    event_title.click()
                    if self.device(description="Delete event").wait.exists(timeout=3000):
                        self.device(description="Delete event").click()
                    if self.device(text="OK").wait.exists(timeout=1000):
                        self.device(text="OK").click()
                else:
                    break
            # else:
            #     self.back_to_home()
            #     self.enter_calendar()
            self.logger.info("delete all the events successfully")
        except:
            self.logger.warning(traceback.format_exc())

    def enter_alarm(self):
        '''Launch alarm by start activity.
        '''
        alarm_tab = self.device(textMatches="Alarm|ALARM")
        if alarm_tab.exists:
            alarm_tab.click()
            self.device.delay(1)
            return True

        self.start_app("Clock")
        if alarm_tab.exists:
            alarm_tab.click()
            self.device.delay(1)
            return True

        return False

    def add_alarm(self):
        """add an alarm without change.
        """
        if self.device(packageName="com.google.android.deskclock").exists:
            package_name = "com.google.android.deskclock"
        else:
            package_name = "com.android.deskclock.bb"

        self.logger.debug("Add an alarm without change.")
        # self.device(resourceId="com.google.android.deskclock:id/sliding_tabs").child(index=0).child(index=0).click.wait(timeout=2000)
        self.device(resourceId=package_name + ":id/fab").click()
        self.device(text="OK").click.wait(timeout=2000)
        self.device(resourceId=package_name + ":id/arrow").click.wait(timeout=2000)
        for i in range(3):
            if not self.device(resourceId=package_name + ":id/onoff", checked=True).exists:
                break
            self.device(resourceId=package_name + ":id/onoff", checked=True).click()
            self.device.delay(1)
            self.logger.debug('Add an alarm successfully.')
            return True
        self.logger.debug('alarm add fail!')
        self.save_fail_img()
        return False

    def add_alarm_tct(self):
        """
        add an alarm without change for TCT one
        :return:
        """
        # if self.device(packageName="com.google.android.deskclock").exists:
        #     package_name = "com.google.android.deskclock"
        # else:
        #     package_name = "com.android.deskclock:id/fab"

        self.logger.debug("Add an alarm without change.")
        self.add_new_btn.click()
        self.device.wait.idle()
        time.sleep(1)
        if self.device(resourceId="com.android.deskclock:id/toolbar_confirm_btn").exists:
            self.device(resourceId="com.android.deskclock:id/toolbar_confirm_btn").click()
        self.device.wait.idle()

        # verify
        if not self.is_no_alarm(self.alarm_item):
            self.logger.info('Add an alarm successfully.')
            return True
        self.logger.error('alarm add fail!')
        self.save_fail_img()
        return False

    def add_alarm2(self):
        """
        add alarm for next 10m
        :return:
        """
        self.logger.info("Add an alarm for next 10m")
        self.device(resourceId="com.android.deskclock.bb:id/fab").click()

        # set time
        self._set_start_time()

    def delete_alarm(self):
        '''Delete alarm.        
        '''
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
        self.logger.debug('delete all alarms')
        no_alarms_texts = [self.device(text="No alarms"), self.device(text="No Alarms")]
        found = False
        for i in range(10):
            for text in no_alarms_texts:
                if text.exists:
                    self.logger.info("delete all alarms success")
                    found = True
                    break
            if found:
                return True

            if self.device(description="Expand alarm").wait.exists():
                self.device(description="Expand alarm").click.wait()
                self.device(resourceId="com.google.android.deskclock:id/delete").click.wait()
            elif self.device(description="Collapse alarm").wait.exists():
                self.device(resourceId="com.google.android.deskclock:id/delete").click.wait()

            self.device.delay(2)
        self.logger.info("alarms more than 10")
        self.save_fail_img()
        return False

    def delete_alarm_tct(self):
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
        self.logger.debug('delete all alarms')

        self.device.delay(2)
        # el = self.device(resourceId="com.android.deskclock:id/digital_clock")
        count = self.get_alarm_num(self.alarm_item)
        if self.is_no_alarm(self.alarm_item):
            return True
        for i in range(count):
            if self.alarm_item.exists:
                self.device.delay (2)
                self.alarm_item.click()
                self.device.wait.idle()
                self.device.delay (2)
                self.device(text="Delete").click()
                self.device.delay(2)
                self.device(text="OK").click()
                self.device.wait.idle()
                self.device.delay (2)

        if self.is_no_alarm(self.alarm_item):
            return True

        self.save_fail_img()
        return False

    def is_no_alarm(self, el):
        count = self.get_alarm_num(el)
        if count == 0:
            self.logger.info("no alarm to delete")
            return True
        self.logger.info("found alarm {}".format(count))
        return False

    def get_alarm_num(self, _device):
        count = _device.count
        return count

    def enter_wclock(self):
        '''Launch world clock by start activity.
        '''
        # add 2 resource id here, always changed in different branch
        clock_tab = self.device(text="CLOCK")
        clock_tab2 = self.device(description="Clock")
        if clock_tab.exists:
            clock_tab.click()
            self.device.delay(1)
            return True
        self.start_app("Clock")
        if clock_tab.wait.exists(timeout=2000):
            clock_tab.click()
            self.device.delay(1)
            return True
        elif clock_tab2.exists:
            clock_tab2.click()
            self.device.delay(1)
            return True
        else:
            return False

    def get_wclock_num(self):
        if self.device(resourceId="com.android.deskclock:id/city_name").exists:
            count = self.device(resourceId="com.android.deskclock:id/city_name").count
        elif self.device(resourceId="com.android.deskclock.bb:id/city_name").exists:
            count = self.device(resourceId="com.android.deskclock.bb:id/city_name").count
        else:
            count = self.device(resourceId="com.google.android.deskclock:id/city_name").count

        count = count - 1 if self.device(text="Home").exists else count
        return count

    def add_wclock(self):
        """add world clock without change.
        """
        # self.device(resourceId="com.google.android.deskclock:id/sliding_tabs").child(index=0).child(index=1).click.wait(timeout=2000)
        self.logger.debug("Add two world clocks without change.")
        self.delete_wclock()
        # cities = ['Islamabad', 'Vancouver', 'Kyiv', 'Seattle']
        cities = ['US', 'UK']
        city2 = random.sample(cities, 2)
        if self.device(resourceId="com.google.android.deskclock:id/fab").exists:  # GMS clock
            for i in range(len(city2)):
                self.device(resourceId="com.google.android.deskclock:id/fab").click()
                self.device(resourceId="com.google.android.deskclock:id/search_src_text").set_text(city2[i])
                # self.device.wait.idle()
                self.logger.info("wait 15s for searching.......")
                self.device.delay(15)  # search something take more time
                self.device(resourceId="com.google.android.deskclock:id/city_name").click.wait()
                self.device.delay()

            # self.device(resourceId="com.google.android.deskclock:id/cities_list").child(index=0).click.wait(
            #     timeout=2000)
            # self.device(resourceId="com.google.android.deskclock:id/cities_list").child(index=4).click.wait(
            #     timeout=2000)
            # self.device.delay(1)
            # self.device.press.back()
            # if not self.device(resourceId="com.google.android.deskclock:id/search_button").wait.gone(timeout=1000):
            #     self.device.press.back()
        else:
            self.device(resourceId="com.android.deskclock.bb:id/fab").click()
            self.device(resourceId="com.android.deskclock.bb:id/cities_list").child(index=0).click.wait(timeout=2000)
            self.device(resourceId="com.android.deskclock.bb:id/cities_list").child(index=4).click.wait(timeout=2000)
            self.device.delay(1)
            self.device.press.back()
            if not self.device(resourceId="com.android.deskclock.bb:id/search_button").wait.gone(timeout=1000):
                self.device.press.back()

        self.device.delay(1)
        if self.get_wclock_num() >= 2:
            self.logger.debug('Add two world clocks successfully.')
            return True
        else:
            self.logger.debug('world clocks add fail!')
            self.save_fail_img()
            return False

    def add_wclock_tct(self, city2):
        self.logger.debug("Add two world clocks without change.")
        # self.delete_wclock_tct()
        # cities = ['Abidjan', 'Accra', 'Amman', 'Anadyr']
        # city2 = random.sample(cities, 2)

        self.add_new_btn.click()
        self.device.wait.idle()
        print city2
        for city in city2:
            self.device(text=city).click()
            self.device.wait.idle()
        self.device.press.back()
        self.device.delay(1)

        # verify
        if all(self.device(text=city).wait.exists(timeout=1000) for city in city2):
            return True

        self.logger.error("******* add word clock failed ******")
        self.save_fail_img()
        return False

    def delete_wclock_tct(self, city2):
        self.logger.debug('delete all world clocks')

        self.add_new_btn.click()
        self.device.wait.idle()

        for city in city2:
            self.device(text=city).click()
            self.device.wait.idle()
        self.device.press.back()
        self.device.delay(1)

        # verify
        if all(not self.device(text=city).wait.exists(timeout=1000) for city in city2):
            return True

        self.logger.error("******* del word clock failed ******")
        self.save_fail_img()
        return False

    def delete_wclock(self):
        '''Delete world clocks.
        '''
        self.logger.debug('delete all world clocks')
        # if self.device(packageName="com.google.android.deskclock").exists:
        #     package_name = "com.google.android.deskclock"
        # else:
        #     package_name = "com.android.deskclock.bb"
        # self.device(resourceId=package_name + ":id/fab").click()
        # self.device.delay(2)
        # for i in range(5):
        #     if not self.device(resourceId=package_name + ":id/city_onoff", checked=True).exists:
        #         break
        #     else:
        #         self.device(resourceId=package_name + ":id/city_onoff", checked=True).click()
        #         self.device.delay(2)
        # self.device.press.back()
        # if not self.device(resourceId=package_name + ":id/search_button").wait.gone(timeout=1000):
        #     self.device.press.back()
        # self.device.delay(1)
        loops = self.get_wclock_num()
        self.logger.debug('found %s world clocks' % loops)
        for i in range(loops):
            # self.device(resourceId="com.google.android.deskclock:id/selectable_area").\
            #     drag.to(resourceId="com.google.android.deskclock:id/trash")
            # self.device(resourceId="com.google.android.deskclock:id/selectable_area").drag.to(x=357, y=1382)
            self.device.long_click(530, 973)
            self.device.swipe(530, 973, 530, 2067)
            self.device.delay()

        if self.get_wclock_num() == 0:
            self.logger.debug('Delete world clocks successfully.')
            return True
        else:
            self.logger.debug('delete world clocks fail!')
            self.save_fail_img()
            return False

    def enter_note(self):
        """Launch Notes by StartActivity.
        """
        self.logger.debug('enter Notes')
        if self.device(packageName="com.tct.note").wait.exists(timeout=5000):
            return True
        self.start_app("Notes")
        if self.device(packageName="com.tct.note").wait.exists(timeout=5000):
            return True

    def get_note_num(self):
        return self.device(resourceId="com.tct.note:id/grid_item").count

    def add_note(self, name):
        """add a note.
        """
        self.logger.debug("Add a note with attachment.")
        self.device(resourceId="com.tct.note:id/newadd_btn2").click()
        self.device.delay(2)
        self.device(resourceId='com.tct.note:id/editview').set_text(name)
        self.device(description="Attachments").click.wait(timeout=1000)
        self.device(text="Gallery").click.wait(timeout=1000)
        self.device(resourceId="com.android.documentsui:id/grid").child(index=0).click.wait(timeout=1000)
        self.device(resourceId="com.tct.note:id/done_menu_item").click.wait(timeout=1000)
        self.device.delay(1)
        if self.get_note_num() >= 1:
            self.logger.debug('Add the note successfully.')
            return True
        else:
            self.logger.debug('Note add fail!')
            self.save_fail_img()
            return False

    def check_note(self, name):
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
            self.device(scrollable=True).scroll.vert.to(textStartsWith=name)
        if self.device(textStartsWith=name).wait.exists(timeout=10000):
            self.device(textStartsWith=name).click()
            if self.device(textStartsWith=name).wait.exists(timeout=10000):
                self.logger.debug('check the note successful')
                self.device.press.back()
                return True
        else:
            self.logger.debug('check fail')
            self.save_fail_img()
            return False

    def delete_note(self, name=None):
        if self.device(scrollable=True).exists:
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10)
        self.logger.debug('Clean up all the notes')
        for i in range(5):
            if self.device(text="No notes").exists:
                self.logger.info('Clean up all the notes success')
                return True
            self.device(resourceId="com.tct.note:id/card_layout").click()
            self.device(resourceId="com.tct.note:id/view_delete").click()
            self.device(text="OK").click()
            self.device.delay(2)
        self.logger.info("notes more than 5s")
        self.save_fail_img()
        return False

    def add_del_note(self, times=1):
        self.logger.debug('Add and delete note ' + str(times) + ' Times')
        self.enter_note()
        for loop in range(times):
            name = random_name(loop)
            try:
                if self.add_note(name) and self.check_note(name) and self.delete_note():
                    self.suc_times += 1
                    self.logger.info("Trace Success Loop " + str(loop + 1))
            except Exception, e:
                self.logger.info(e)
                self.save_fail_img()
                self.delete_note()
        self.back_to_home()
        self.logger.debug('Add and delete note Test complete')

    def is_account_enrolled(self, account):
        """
        check the given account is enrolled or not, you should back to home of calendar manually
        :return:
        """
        self._go_to_menu()
        return self.device(text=account).wait.exists(timeout=3000)

    def create_invite(self, account_from, account_to, invite_title, reminder_option="5 minutes"):
        """
        create invite to second account
        :param account_to:
        :return:
        """
        self.logger.info("start create invite, from %s to %s." % (account_from, account_to))
        if not self.device(resourceId="com.blackberry.calendar:id/home_activity_drawer_content").wait.exists(
                timeout=3000):
            self._go_to_menu()
        # click agenda
        assert self.device(resourceId="com.blackberry.calendar:id/home_activity_drawer_content").wait.exists(
            timeout=3000), "can not find menu list"
        assert self.device(text="Agenda").wait.exists(), "******** can not find Agenda ********"
        self.device(text="Agenda").click.wait(timeout=3000)

        # click action today
        assert self.device(description="Navigation Drawer Open").wait.exists(timeout=3000)
        self._click_action_today()

        # create invite
        create_btn = self.device(resourceId="com.blackberry.calendar:id/create_event_fan_root_fab")
        if create_btn.wait.exists():
            create_btn.click.wait(timeout=3000)

        event = self.device(resourceId="com.blackberry.calendar:id/new_event_button")
        assert event.wait.exists(), "******** can not find new event btn  ********"
        event.click.wait(timeout=3000)

        # todo: check account

        self._check_account(account_from)

        # set title
        assert self.device(resourceId="com.blackberry.calendar:id/title").wait.exists(timeout=3000)
        self.device(resourceId="com.blackberry.calendar:id/title").set_text(invite_title)

        # set start time
        assert self.device(resourceId="com.blackberry.calendar:id/start_time").wait.exists(timeout=3000)
        self.device(resourceId="com.blackberry.calendar:id/start_time").click.wait()
        self._set_start_time()

        # add contact
        self.device.delay(1)
        add_contact = self.device(resourceId="com.blackberry.calendar:id/tagTextViewContainer")
        assert add_contact.wait.exists(), "******** can not find add contact btn  ********"
        add_contact.click.wait(timeout=3000)
        # it will fail to input the first character if without DEL in Athena
        self.adb.shell("input keyevent KEYCODE_DEL")
        self.device.wait("idle")
        self.adb.shell("input text %s" % account_to)
        self.adb.shell("input keyevent KEYCODE_ENTER")

        # set notification reminder
        self.device.delay(2)
        reminder = self.device(resourceId="com.blackberry.calendar:id/reminder_minutes_value")
        assert reminder.wait.exists(), "******** can not find reminder  ********"
        reminder.click.wait(timeout=3000)

        # select 5 min
        assert self.device(
            resourceId="android:id/select_dialog_listview").wait.exists(), "******** can not find list view for reminder  ********"
        self.device(resourceId="android:id/select_dialog_listview").scroll.vert.toBeginning(steps=100, max_swipes=100)
        five_min = self.device(text=reminder_option)
        assert five_min.wait.exists(), "******** can not find %s option ********" % reminder_option
        five_min.click.wait(timeout=3000)

        # assert back to event creation activity, and click save btn
        save = self.device(resourceId="com.blackberry.calendar:id/action_done")
        assert save.wait.exists(), "******** can not find save btn  ********"
        save.click.wait(timeout=3000)

        # set default calendar if needed
        if self.device(text="Set default calendar").wait.exists(timeout=3000):
            if self.device(text="Don't show this again").wait.exists(timeout=1000):
                self.device(text="Don't show this again").click()
            self.device(text="YES").click.wait()

    def _check_account(self, account_from):
        if self.device(resourceId="com.blackberry.calendar:id/calendar_owner", text=account_from).ext5:
            self.logger.debug("default select account is %s" % account_from)
            return True

        self.logger.debug("try to select account  %s" % account_from)
        if self.device(resourceId="com.blackberry.calendar:id/calendar_selected_item").ext5:
            self.device(resourceId="com.blackberry.calendar:id/calendar_selected_item").click()

        count = self.device(className="android.widget.ListView", packageName="com.blackberry.calendar").info[
            "childCount"]
        print "count:", count
        for loop in range(count):
            item = self.device(resourceId="com.blackberry.calendar:id/calendar_selected_item", index=loop)
            if item.ext5:
                if item.child(resourceId="com.blackberry.calendar:id/calendar_owner").wait.exists(timeout=10000):
                    accountName = item.child(resourceId="com.blackberry.calendar:id/calendar_owner").get_text()
                # else:
                #     self.logger.debug("can not get accountName,return false")
                #     self.save_fail_img()
                #     return False

                if accountName == account_from:
                    self.logger.debug("%s match %s" % (accountName, account_from))
                    index = loop + 1
                    if self.device(resourceId="com.blackberry.calendar:id/calendar_selected_item", index=index).ext5:
                        self.logger.debug("select %s successfully" % account_from)
                        self.device(resourceId="com.blackberry.calendar:id/calendar_selected_item", index=index).click()
                        return True
                else:
                    self.logger.debug("%s did not match %s,try another one." % (accountName, account_from))
        self.logger.debug("select account %s failed" % account_from)

    def _click_action_today(self):
        assert self.device(
            resourceId="com.blackberry.calendar:id/action_today").wait.exists(), "******** can not find action today  ********"
        self.device(resourceId="com.blackberry.calendar:id/action_today").click.wait(timeout=3000)
        self.device.delay(1)
        self.device(resourceId="com.blackberry.calendar:id/action_today").click.wait(timeout=3000)

    def _go_to_menu(self):
        """go to calendar menu
        """
        menu = self.device(description="Navigation Drawer Open")
        assert menu.wait.exists(), "******** can ont find menu  ********"
        menu.click.wait(timeout=3000)
        menu.wait.gone(timeout=3000)

    def _set_start_time(self):
        """
        get current time, add 10m,
        :return:
        """
        # get current time
        current_time, err = self.adb.shell2("date +%I:%M")
        print "current_time is %s" % current_time
        assert ":" in current_time, "****** get current time(%s) failed *****" % current_time
        h, m = int(current_time.split(":")[0]), int(current_time.split(":")[1])
        target_h = h
        target_m = m + 5 - (m % 5)
        # target_m = m + 2
        if target_m >= 60:
            target_m -= 60
            target_h += 1

        target_h = str(target_h)
        target_m = str(target_m)
        print "target_time is %s:%s" % (target_h, target_m)

        # if self.device(resourceId="android:id/toggle_mode").ext5:
        #     self.device(resourceId="android:id/toggle_mode").click()
        #
        # if self.device(resourceId="android:id/input_hour").ext5:
        #     self.device(resourceId="android:id/input_hour").set_text(target_h)
        # if self.device(resourceId="android:id/input_minute").ext5:
        #     self.device(resourceId="android:id/input_minute").set_text(target_m)
        # if int(target_h)>12:
        #     if self.device(resourceId="android:id/am_pm_spinner").ext5:
        #         self.device(text="PM").click
        # if self.device(text="OK").exists:
        #     self.device(text="OK").click()

        self.logger.debug("set target time %s:%s completed" % (target_h, target_m))
        hour_picker = self.device(className="android.widget.RadialTimePickerView$RadialPickerTouchHelper",
                                  description=target_h)
        assert hour_picker.wait.exists(), "******** can not find hour picker  ********"
        hour_picker.click.wait(timeout=3000)

        min_picker = self.device(className="android.widget.RadialTimePickerView$RadialPickerTouchHelper",
                                 description=target_m)
        assert min_picker.wait.exists(), "******** can not find min picker  ********"
        min_picker.click.wait(timeout=3000)
        ####click OK, finish creation
        self.device.delay(1)
        ok_btn = self.device(text="OK")
        assert ok_btn.wait.exists(), "******** can not find ok btn  ********"
        ok_btn.click.wait(timeout=3000)

    def accept_invite(self):
        self.logger.info("starting to accept invite")

        # accept invite
        accept = self.device(resourceId="com.blackberry.calendar:id/view_event_fragment_response_bar_accept_button")
        assert accept.wait.exists(), "******** can not find YES btn to accept invite  ********"
        accept.click.wait(timeout=3000)

        # confirm
        confirm = self.device(resourceId="com.blackberry.calendar:id/calendar_dialog_ok_button")
        assert confirm.wait.exists(), "******** can not find OK btn  ********"
        confirm.click.wait(timeout=3000)

    def observe_reminder(self, title, account_to):
        """
        observe reminder,
        :return:
        """
        self.logger.info("observe reminder in notification")

        # wait for notification in 15min
        # if self.device(textStartsWith=title, packageName="com.blackberry.calendar").wait.exists(timeout=10 * 60 * 1000):
        #     assert self.device(text="SNOOZE").wait.exists(timeout=3000)

        if self.device(text=account_to).wait.exists(timeout=2 * 60 * 1000):
            self.logger.debug("Receive an email with the title '%s' from %s" % (title, account_to))
            if self.device(text="DELETE").ext5:
                self.device(text="DELETE").click()
                self.logger.debug("Delete the email")
            if self.device(text="DELETE").ext5:
                self.device(text="DELETE").click()

        self.device.open.notification()
        calendar_node = self.device(text="Calendar")
        if calendar_node.wait.exists(timeout=6 * 60 * 1000):
            if self.device(text="Meeting Mode is Available").exists:
                self.device.swipe(890, 545, 123, 545, 20)
                self.device.wait("idle")
            assert calendar_node.wait.exists(timeout=10 * 60 * 1000), "can't find calendar node"
        else:
            self.logger.debug("calendar_node not exists")

        calendar_text = calendar_node.down(textContains=title)
        if calendar_text.ext5:
            calendar_expand_text = calendar_node.sibling(description="Expand")
            if calendar_expand_text.exists:
                self.logger.debug("click Expand")
                calendar_expand_text.click.wait()

            assert self.device(text="SNOOZE", packageName="com.android.systemui").ext5 and self.device(
                text="Calendar").ext5, "can not receive the calendar notification"

    def observe_reminder_accept(self, title):
        """
        this method is NOT BEST implementation
        observe reminder for accepted mail,
        uiautomator can not find element via text, the text is bord? not sure
        the notification must be the first one, otherwise the resource id will be changed....
        :return:
        """
        new_title_regular = '^Accepted:.*%s' % title

        get_title = ""

        ##如果通知栏有多个相似通知，resourceId="android:id/title"取到的是最后一个，导致测试失败，所以需要取第一个通知
        ##同步有点慢，所以需要在5分钟内判断是否存在

        start_time = time.time()
        while self.time_task(start_time, 5 * 60):
            if self.device(className="android.widget.FrameLayout", packageName="com.android.systemui").ext5:
                childCount = self.device(resourceId="com.android.systemui:id/notification_stack_scroller").childCount
                print "'com.android.systemui:id/notification_stack_scroller' has %s child:" % childCount

            for loop in range(childCount):
                title_text_element = self.device(className="android.widget.FrameLayout",
                                                 packageName="com.android.systemui", index=loop).child(
                    resourceId="android:id/big_text")

                title_text_element_variant = self.device(className="android.widget.FrameLayout",
                                                         packageName="com.android.systemui", index=loop).child(
                    resourceId="com.android.systemui:id/notification_text")
                if title_text_element.ext5:
                    title_name = title_text_element.get_text()
                elif title_text_element_variant.ext5:
                    title_name = title_text_element.get_text()
                print "get the %d  title:%s" % (loop, title_name)
                isExists = re.search(new_title_regular, title_name)
                if isExists:
                    title = isExists.group()
                    self.logger.debug("find '%s'" % title)
                    return True
            time.sleep(2)
        # assert self.device(textStartsWith=new_title).wait.exists(timeout=6000), "can not find %s" % new_title
        else:
            raise ValueError("can not find '%s'" % new_title_regular)

    def snooze_1_min(self):
        """
        snooze 1 min
        :return:
        """
        # assert self.device(text="SNOOZE").wait.exists(timeout=3000)
        # self.device(text="SNOOZE").click.wait()
        self.logger.debug("starting to snooze 1 min")
        assert self.device(text="SNOOZE", packageName="com.android.systemui").wait.exists(timeout=3000)
        self.device(text="SNOOZE", packageName="com.android.systemui").click.wait()

        # select 1 min in snooze 
        assert self.device(
            resourceId="com.blackberry.calendar:id/custom_snooze_dialog_banner").wait.exists(), "******** can not find snooze dialog  ********"
        min_1 = self.device(text="1 minute")
        assert min_1.wait.exists(), "******** can not find 1 minute option  ********"
        min_1.click.wait(timeout=3000)

        # confirm
        OK_btn = self.device(resourceId="com.blackberry.calendar:id/custom_snooze_dialog_ok_button")
        assert OK_btn.wait.exists(), "******** can not find OK btn to confirm snooze 1 min  ********"
        OK_btn.click.wait(timeout=3000)

    def open_invite(self, title):
        """
        search invite
        :param title:
        :return:
        """
        # del invite for title, from beginning
        if not self.device(resourceId="com.blackberry.calendar:id/commonui_search_menu_button").wait.exists(
                timeout=3000):
            self.device.press.home()
            self.enter_calendar()

        search_btn = self.device(resourceId="com.blackberry.calendar:id/commonui_search_menu_button")
        assert search_btn.wait.exists(), "******** can not find search btn  ********"
        search_btn.click.wait(timeout=3000)

        assert self.device(
            resourceId="android:id/search_src_text").wait.exists(), "******** can not open search  ********"
        self.device(resourceId="android:id/search_src_text").set_text(title)

        # assert event exist
        event = self.device(text=title, resourceId="com.blackberry.calendar:id/title")
        assert event.wait.exists(), "******** can not find event: %s ********" % title
        event.click.wait(timeout=3000)
        if (not self.device(
                resourceId="com.blackberry.calendar:id/view_event_menu_delete_event_action").wait.exists()) and event.exists:
            event.click.wait()

    def delete_invite(self, title):
        """
        delete invite
        :param title:
        :return:
        """
        self.open_invite(title)
        self._click_del()

        assert not self.device(text=title, resourceId="com.blackberry.calendar:id/title").wait.exists(
            timeout=3000), "***** invite del failed *****"

    def _click_del(self):
        del_btn = self.device(resourceId="com.blackberry.calendar:id/view_event_menu_delete_event_action")
        assert del_btn.wait.exists(), "******** can not find del btn  ********"
        del_btn.click.wait(timeout=3000)

        # confirm
        ok_btn = self.device(resourceId="com.blackberry.calendar:id/calendar_dialog_ok_button")
        assert ok_btn.wait.exists(), "******** can not find OK btn ********"
        ok_btn.click.wait(timeout=3000)

    def enter_task(self):
        '''Launch task by start activity.
        '''
        if self.device(resourceId="com.blackberry.tasks:id/signature_fab").wait.exists(timeout=5000):
            self.logger.debug("Task is already open.")
            return True
        for loop in range(5):
            if self.start_app("Tasks"):
                break
            self.logger.debug("open Tasks again")
        if self.device(resourceId="com.blackberry.tasks:id/signature_fab").wait.exists(timeout=5000):
            self.logger.debug("open Task successfully.")
            return True

        self.logger.debug("open Task failed!!!")
        return False

    def delete_task(self):
        """delete task in task app"""
        for i in range(10):
            self.logger.debug("delete task")
            if self.device(resourceId="com.blackberry.tasks:id/task_list_item_layout").wait.exists():
                self.device(resourceId="com.blackberry.tasks:id/task_list_item_layout").long_click()
                if self.device(resourceId="com.blackberry.tasks:id/menu_delete").wait.exists():
                    self.device(resourceId="com.blackberry.tasks:id/menu_delete").click.wait()
                    self.device.delay(2)
            else:
                self.logger.debug("delete task finish")
                return True

    def create_task(self, name):
        self.logger.debug('create a new task %s' % name)

        # when using same account in all DUT, maybe will sync failed, using local tack instead
        if self.device(description="Open navigation drawer").wait.exists(timeout=3000):
            self.device(description="Open navigation drawer").click()
            if self.device(text="Local Tasks").wait.exists(timeout=3000):
                self.device(text="Local Tasks").click()

        if self.device(resourceId="com.blackberry.tasks:id/signature_fab").wait.exists(timeout=5000):
            self.device(resourceId="com.blackberry.tasks:id/signature_fab").click()

        if self.device(resourceId="com.blackberry.tasks:id/task_detail_subject").wait.exists(timeout=5000):
            self.device(resourceId="com.blackberry.tasks:id/task_detail_subject").set_text(name)

        if self.device(resourceId="com.blackberry.tasks:id/property_edit_default_text").wait.exists(timeout=5000):
            self.device(resourceId="com.blackberry.tasks:id/property_edit_default_text").click()

        if self.device(text="OK").wait.exists(timeout=5000):
            self.device(text="OK").click()

        el = self.device(resourceId='com.blackberry.tasks:id/menu_save')
        el.click.wait()
        if self.device(description="Navigate up").wait.exists(timeout=5000):
            self.device(description="Navigate up").click()

        if self.device(text=name).wait.exists(timeout=10000):
            self.logger.info('create a new task %s success' % name)
            return True

        self.logger.info('create a new task %s failed' % name)
        self.save_fail_img()
        return False

    def click_save_btn(self):
        save_btn = self.device(textMatches="Save|SAVE")
        save_btn.click()

    def enter_google_calendar(self):
        self.start_app('Calendar')
        el = self.device(resourceId="com.google.android.calendar:id/right_arrow")
        en = self.device(resourceId="com.google.android.calendar:id/next_arrow")
        done_b=self.device(resourceId="com.google.android.calendar:id/done_button")
        # for i in range(3):
        #     if self.device(resourceId="com.google.android.calendar:id/done_button").exists:
        #         self.device (resourceId="com.google.android.calendar:id/done_button").click()
        #         break
        #     elif el.exists:
        #         el.click()
        #     elif en.exists:
        #         en.click()
        if self.device(text="Make the most of every day.").wait.exists(timeout=3000):
            while True:
                if el.exists:
                    el.click()
                elif en.exists:
                    en.click()
                elif done_b.exists:
                    done_b.click()
                    break
        # el = self.device(resourceId="com.google.android.calendar:id/done_button")
        # if el.wait.exists(timeout=3000):
        #     el.click()
        if self.device(text="Dismiss").wait.exists(timeout=10000):
            self.device(text="Dismiss").click()
        time.sleep(1)
        self.device(resourceId="com.google.android.calendar:id/floating_action_button").click()
        if self.device(text="Event").exists:
            self.device (text="Event").click()
        self.device(scrollable=True).scroll.vert.to(text="Add location")
        self.device(text="Add location").click()
        time.sleep(1)
        if self.device(text="ALLOW ONLY WHILE USING THE APP").exists:
            self.device (text="ALLOW ONLY WHILE USING THE APP").click ()
        self.back_to_home()

    def setup(self):
        self.enter_google_calendar()



if __name__ == '__main__':
    a = Schedule("GAWKFQT8WGL7L7S8", "Schedule")
    # a.enter_calendar()
    a.setup()
