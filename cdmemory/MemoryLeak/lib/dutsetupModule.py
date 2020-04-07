# -*- coding: UTF-8 -*-
import re, random, sys, traceback
from lib import common
from lib.common import Common
from pydoc import classname

settings_package="com.android.settings"
settings_activity=".Settings"
call_package = 'com.google.android.dialer'
call_activity = '.extensions.GoogleDialtactsActivity'
message_package='com.google.android.apps.messaging'
message_activity='.ui.ConversationListActivity'
camera_package='com.tcl.camera'
camera_activity='com.android.camera.CameraLauncher'
contact_package='com.google.android.contacts'
contact_activity='com.android.contacts.activities.PeopleActivity'

class DutSetup (Common):
	"""Provide common functions involved call."""

	def __init__(self, device, log_name="Setup"):
		Common.__init__ (self, device, log_name)

	def call_module_speedDial(self,num="10010"):
		self._logger.debug("Set call speedDial")
	def enter_call(self):
		self._logger.debug ("Launch Call.")
		self._device.start_activity (call_package, call_activity)
		self._device.delay (2)
		if self._device (text="OK, got it").exists:
			self._device (text="OK, got it").click ()
			self._device.delay (2)
		if self._device.currentPackageName == call_package:
			self._logger.debug ("Launch Call Success")
			return True
		return False

	def isInCall(self):
		for _ in range (10):
			if self._device (resourceId="com.google.android.dialer:id/contactgrid_bottom_timer").exists:
				return True
			callState = self._device.get_call_state ()
			if callState == "incall":
				return True
			self._device.delay (2)
		return False

	def end_call(self):
		self._logger.info ("End the call")
		endBtn = self._device (resourceId="com.tct.dialer:id/incall_end_call")
		if endBtn.exists:
			endBtn.click.wait ()
			self._device.delay (3)
		elif self._device (resourceId="com.google.android.dialer:id/contactgrid_bottom_timer").exists:
			self._device.shell_adb ("shell input keyevent KEYCODE_ENDCALL")
		elif self._device.get_call_state () == "incall" or self._device.get_call_state () == "ringing":
			self._device.shell_adb ("shell input keyevent KEYCODE_ENDCALL")
			self._device.delay (1)
		else:
			self._device.delay (1)
			return
		self._logger.info ("Wait for 10s before next call...")
		self._device.delay (10)
		if self._device (text="Say why you called").exists:
			self._device (text="No, thanks").click ()
		if self._device.get_call_state () == "idle":
			self._logger.info ('End the call successful!')

	def callFromSpeedDial(self):
		self._logger.info ("Call From SpeedDial.")
		for _ in range (5):
			if self._device (description="Call history").exists:
				self._device (description="Call history").click ()
			# google dialer
			elif self._device (text="Recents").exists:
				self._device (text="Recents").click ()
			if self._device (resourceId="com.google.android.dialer:id/fab", description="key pad").exists:
				break
		if self._device (resourceId="com.google.android.dialer:id/fab", description="key pad").exists:
			self._device (resourceId="com.google.android.dialer:id/fab", description="key pad").click.wait ()
			self._device.delay (1)
		self._device (resourceId="%s:id/dialpad_key_number" % call_package, text="2").long_touch ()
		self._device.delay (8)
		if self.isInCall ():
			self._logger.debug ('Outgoing call success from dialer')
			self.end_call ()
			return True
		self._logger.debug ('Outgoing call fail from dialer')
		self.end_call ()
		return False

	def callFromDialPad(self, dialNumber="10010"):
		if self.isInCall ():
			self.end_call ()
		self._logger.info ("Call From DialPad.")
		if not self._device (text="Recents").isSelected ():
			self._device (text="Recents").click.wait ()
			self._device.delay (1)
		self._device (resourceId="com.google.android.dialer:id/fab").click.wait ()
		self._device.delay (1)
		self._logger.debug ("Dial Number %s." % dialNumber)
		digitsItem = self._device (resourceId='%s:id/digits' % call_package)
		if digitsItem.exists:
			digitsItem.set_text (dialNumber)
		else:
			num = list (dialNumber)
			for i in num:
				self._device (text=i).click ()
				self._device.delay (1)
		self._device (resourceId="com.google.android.dialer:id/dialpad_floating_action_button").click.wait ()
		self._device.delay (2)
		self.end_call ()

	def callFromContacts(self, _index=0):
		self._logger.debug ('make call from contact ')
		if not self._device (text="Contacts").isSelected ():
			self._device (text="Contacts").click.wait ()
			self._device.delay (2)
		if self._device (resourceId="com.google.android.dialer:id/contact_name", instance=2).exists:
			self._device (resourceId="com.google.android.dialer:id/contact_name", instance=2).click.wait ()
			self._device.delay (2)
		if self._device (resourceId="com.tct.dialer:id/cliv_name_textview", instance=2).exists:
			self._device (resourceId="com.tct.dialer:id/cliv_name_textview", instance=2).click.wait ()
			self._device.delay (2)
		elif self._device (text="ABCD 2").exists:
			self._device (text="ABCD 2").click.wait ()
			self._device.delay (2)
		else:
			self._logger.debug ('The contacts not exists in phonebook!')
			return False
		dialIcon = self._device (resourceId="com.tct.dialer:id/header")
		dialIcon.click.wait ()
		self._device.delay (4)
		self.end_call ()
		self._device.press ("back")

	def callFromDifMode(self):
		self._logger.debug ("Start to Call from different mode.")
		if not self.enter_call ():
			self.enter_call ()
		try:
			self.callFromSpeedDial ()
			self.callFromDialPad ()
			self.callFromContacts ()
			if self._device (resourceId="com.tct.dialer:id/search_box_start_search").exists:
				self._logger.info ("callFromDifMode is successful.")
				self.backToHome ()
				return True
			self.backToHome ()
			return False
		except Exception:
			self.save_fail_img ()
			self._logger.warning ("callFromDifMode Exception!")
			common.log_traceback (traceback.format_exc ())
			self.backToHome ()

	def switchBackAndInvokeFromRecent(self):
		self._logger.debug ("Start to switch back and invoke from recent.")
		if not self.enter_call ():
			self.enter_call ()
		self._device.press ("home")
		self._device.delay (2)
		self._device.press ("recent")
		self._device.delay (2)
		# self._device(className="com.android.systemui.recents.views.TaskStackView").scroll.vert.dto(text="Call+")
		if self._device (resourceId="com.android.launcher3:id/snapshot").exists:
			self._device (resourceId="com.android.launcher3:id/snapshot").click ()
			return True
		self._device.delay (2)
		self.backToHome ()
		return False

	def swipeInCalls(self):
		self._logger.debug ("Start to swipeInCalls.")
		if not self._device (description="Contacts").isSelected ():
			self._device (description="Contacts").click.wait ()
			self._device.delay (2)
		for _ in range (4):
			self._device (resourceId="android:id/list").scroll (steps=100)
			self._device.delay (1)
			self._device (resourceId="android:id/list").scroll (steps=100)
			self._device.delay (1)
			self._device (resourceId="android:id/list").scroll.vert.backward (steps=100)
			self._device.delay (1)
			self._device (resourceId="android:id/list").scroll.vert.backward (steps=100)
			self._device.delay (1)

	def deleteRecentCalls(self):
		self._logger.debug ("Start to deleteRecentCalls.")
		if self._device (description="Call history").exists:
			# print "Start to deleteRecentCalls. 1"
			self._device (description="Call history").click ()
			self._device.delay (1)
		#         if self._device(description="Contacts").exists:
		#             self._device(description="Contacts").click()
		#             self._device.delay(1)
		#         lstItem=self._device(resourceId="com.google.android.dialer:id/recycler_view")
		self._device (resourceId="com.tct.dialer:id/name", instance=0).long_touch ()
		if self._device (description="Delete").exists:
			self._device (description="Delete").click ()
			self._device.delay (1)
		if self._device (text="DELETE").exists:
			self._device (text="DELETE").click ()
			self._device.delay (1)

	def enterDetailsAndCall(self):
		self._logger.debug ("Start to enterDetailsAndCall.")
		if self._device (description="Contacts").exists:
			self._device (description="Contacts").click ()
			self._device.delay (1)
		lstItem = self._device (resourceId="android:id/list")
		lstItem.child (resourceId="com.tct.dialer:id/cliv_name_textview", instance=2).click ()
		self._device.delay (1)
		self._device (descriptionStartsWith="Call").click ()
		self._device.delay (5)
		self.end_call ()
		if self._device (descriptionStartsWith="Call").exists:
			# print "enterDetailsAndCall. 1"
			self._device (description="Navigate up").click ()
			self._device.delay (1)
		else:
			self.save_fail_img ()

	def findAndCheckPhoneNumbers(self, phoneNum="10010"):
		self._logger.info ("Start to findAndCheckPhoneNumbers.")
		for _ in range (5):
			if self._device (description="Call history").exists:
				self._device (description="Call history").click ()
			if self._device (resourceId="com.tct.dialer:id/floating_action_button", description="key pad").exists:
				break
		if self._device (resourceId="com.tct.dialer:id/floating_action_button", description="key pad").exists:
			self._device (resourceId="com.tct.dialer:id/floating_action_button", description="key pad").click.wait ()
			self._device.delay (1)
		self._logger.debug ("Input PhoneNumber %s." % phoneNum)
		#         digitsItem = self._device(resourceId='com.tct.dialer:id/digits')
		#         digitsItem.set_text(phoneNum)
		#         getText=self._device(resourceId="com.vodafone.messaging:id/digits").get_text()
		#         if getText:
		#             self._device(resourceId="com.vodafone.messaging:id/deleteButton").long_touch()
		self.inputNumber (phoneNum)
		#        self._device(resourceId="com.tct.dialer:id/digits_container").set_text(phoneNum)
		self._device.delay (3)
		if self._device (resourceId="com.tct.dialer:id/labelAndNumber", textContains=phoneNum).exists:
			self._logger.debug ("Find out specified PhoneNumber.")
			if self._device (resourceId="com.google.android.dialer:id/deleteButton").exists:
				self._device (resourceId="com.google.android.dialer:id/deleteButton").long_touch ()
			self._device.press ("back")
			self._device.delay (1)
			return True
		return False

	def inputNumber(self, number="10010"):
		numlist = list (number)
		for i in numlist:
			if i == '0':
				self._device (resourceId="com.tct.dialer:id/zero").click ()
			if i == '1':
				self._device (resourceId="com.tct.dialer:id/one").click ()
			if i == '2':
				self._device (resourceId="com.tct.dialer:id/two").click ()
			if i == '3':
				self._device (resourceId="com.tct.dialer:id/three").click ()
			if i == '4':
				self._device (resourceId="com.tct.dialer:id/four").click ()
			if i == '5':
				self._device (resourceId="com.tct.dialer:id/five").click ()
			if i == '6':
				self._device (resourceId="com.tct.dialer:id/six").click ()
			if i == '7':
				self._device (resourceId="com.tct.dialer:id/seven").click ()
			if i == '8':
				self._device (resourceId="com.tct.dialer:id/eight").click ()
			if i == '9':
				self._device (resourceId="com.tct.dialer:id/nine").click ()
			self._device.delay (1)


if __name__ == "__main__":
	d = common.Device ("SGA6VKBUSWIZHI59")
	mCall = Call (d)
	mCall.callFromDialPad ()
	mCall.enter_call ()



