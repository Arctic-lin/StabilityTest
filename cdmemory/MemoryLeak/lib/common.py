# -*- coding: utf-8 -*-
from __future__ import division
import os, unittest, traceback
import sys
import logging
from datetime import datetime
from lib import common
from lib.Uiautomator.uiDevice import UiDevice as Device
from lib.getconfigs import GetConfigs
import time

def createlogger(name): 
    """Create a logger named specified name with the level set in config file.
    """   
    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d: [%(levelname)s] [%(name)s] [%(funcName)s] %(message)s',
        '%y%m%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def create_folder():     
    log_path = os.environ.get("LOG_PATH")
    if log_path is None:
        log_path =  sys.path[0][sys.path[0].find(':')+1:] + '\\results'
    if not os.path.exists(log_path):
        logger.debug("log_path not exsit")
        os.makedirs(log_path)
    if not os.path.exists(log_path):
        return None
    return log_path

def log_traceback(traceback):
    """print traceback information with the log style.
     
    """
    str_list = traceback.split("\n")
    for s in str_list:
        logger.warning(s)

def get_deviceId(device_name): 
    environ = os.environ
    device_id = environ.get(device_name)    
    return device_id

def connect_device(device_name):
    """connect_device(device_id) -> Device    
    Connect a device according to device ID.
    """
    environ = os.environ
    device_id = environ.get(device_name)  
    logger.debug("Device ID is " + str(device_id))
    device = Device(device_id)
    if device is None:
        logger.critical("Cannot connect device.")
        raise RuntimeError("Cannot connect %s device." % device_id)
    return device

logger = createlogger("COMMON")

def runTest(testCaseClass, cases=[]):
    suite = unittest.TestSuite()
    if cases:
        for c in cases:
            suite.addTest(testCaseClass(c))
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(testCaseClass)
    unittest.TextTestRunner().run(suite)

class Common(object):
    
    """Provide common functions for all scripts."""
    
    def __init__(self, device, log_name="COMMON"):
        self._device = device
        self._logger = createlogger(log_name)
        self._config = GetConfigs("common")
        self.unlock()
        if self._device.get_call_state() == "incall":
            self._device.shell_adb("shell input keyevent KEYCODE_ENDCALL")
        self._device.handlers.on(self.uiHandler)
    
    def GetNowTime(self):
        return time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time()))
    
    def uiHandler(self, device):
        self._logger.debug("begin handler")
        if device(textStartsWith="Just a sec").exists or device(text="Couldn't sign in").exists:
            self._logger.debug("GMS handler")
            for _ in range(5):
                if device(text="Next", enabled=True).exists:
                    device(text="Next", enabled=True).click()
                else:
                    break
            else:
                device.press("back")
                device.delay(2)
        elif device(textStartsWith="Unfortunately").exists:
            self._logger.debug("FC and ANR handler enabled")
            self.save_fail_img()
            if device(text="OK").exists:
                device(text="OK").click.wait()
                self._device.delay(1)
        elif self._device(resourceId="com.android.packageinstaller:id/permission_allow_button").exists:
            self._logger.debug("Permission handler enabled")
            print("Permission handler enabled")
            self._device(resourceId="com.android.packageinstaller:id/permission_allow_button").click.wait()
            self._device.delay(2)
        elif self._device(textMatches="(?i)no.*thank.*").exists:
            print("(?i)no.*thank.*")
            self._device(textMatches="(?i)no.*thank.*").click()
            self._device.delay(2)
        elif self._device(textMatches="(?i).*isn't responding.*").exists:
            self._logger.debug("FC and ANR handler enabled")
            self.save_fail_img()
            if device(text="OK").exists:
                self._device(text="OK").click()
                self._device.delay(2)
        elif self._device(textMatches="(?i).*because of an incorrect PIN or password.*").exists:
            self._logger.debug("FC and ANR handler enabled")
            self.save_fail_img()
            if device(text="OK").exists:
                self._device(text="OK").click()
                self._device.delay(2) 
        elif self._device(textMatches="(?i)Mobile network not available.").exists:
            self._logger.debug("FC and ANR handler enabled")
            self.save_fail_img()
            if device(text="OK").exists:
                self._device(text="OK").click()
                self._device.delay(2)
        elif self._device(textMatches="(?i)Sending SMS messages").exists:
            self._logger.debug("FC and ANR handler enabled")
            self.save_fail_img()
            if device(text="ALLOW").exists: 
                self._device(text="OK").click()
            if device(text="Allow").exists:
                device(text="Allow").click()
            self._device.delay(2)					
        return True      
    
    def unlock(self):
        if not self._device.isScreenOn():
            self._device.wakeup()
            self._device.delay(2)
        if self._device.isLocked():
            w = self._device.displayWidth
            h = self._device.displayHeight
            lockIcon = self._device(resourceId="com.android.systemui:id/lock_icon")
            if lockIcon.exists:
                lockIcon.drag.to(x=w/2, y=h/2, steps=5)
        
    def save_fail_img(self, newimg = None):
        """save fail image to log path.        
        argv: The picture want to save as failed image.
        """        
        path = (create_folder() + "\\" +datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".png")
        if newimg is None:
            self._logger.debug("Take snapshot.")
            newimg = self._device.screenshot(path)
        if newimg is None:
            self._logger.warning("newimg is None.")
            return False
        self._logger.error("Fail: %s" %(path))
        return True
    
    def backToHome(self):
        self._logger.info("Back to home.")
        for _ in range(6):
            if self._device(resourceIdMatches=".*id/hotseat").exists:
                return
            self._device.press("back")
            self._device.delay(0.5)
        self._device.delay(1)
        self._device.press("home")
    
    def get_file_num(self, path, _format):
        """get number of file with specified format.
        """        
        content = self._device.shell_adb("shell ls " + path)
#         self._logger.debug('content:'+content)
        num = content.count(_format)
        return num
    
    def task_enter(self):
        self._device.press.recent()
        self._device.delay(2)
        if self._device(resourceId="com.android.systemui:id/title").exists:
            self._logger.debug('Enter task success')
        elif self._device(textContains="No recent items").exists:
            self._logger.debug('Enter task success')  
        else:
            self._logger.debug('Enter task failed')
            return False
        return True
    
    def enterApp(self, appName):
        try:
            self._device.press("home")
            self._device.delay(2)
            self._device(description="Apps").click.wait()
            self._device.delay(1)
            self._device(resourceId="com.android.launcher3:id/apps_list_view").scroll.to(text=appName)
            self._device.delay(1)
            self._device(text=appName).click()
            self._device.delay(2)
        except Exception:
            self.save_fail_img()
            log_traceback(traceback.format_exc())
    
    #获取dump memory info,Begin or End
    def saveMeminfo(self,type = "Begin", packageName = "", filename = ""):
        self._logger.debug('save Memin info')
        content = self._device.shell_adb("shell dumpsys meminfo %s" % packageName)
        dirPath = sys.path[0] + "\\report\\memInfo"
        if not os.path.exists(dirPath):
            os.mkdir(dirPath)
        filename = dirPath +"\\"+ filename + "_"+ packageName + "_" + type + ".txt"
        fp = open(filename,"w+")
        
        fp.write(content)
        
        fp.close()
        
    def clearAllRecent(self):
        self._logger.info("Clear all recent apps")
        try:
            for _ in range(10):
                self._device.press.recent()
                self._device.delay(1)
                if not self._device(resourceId="com.tcl.android.launcher:id/clearAll").exists:
                    self._device.press("home")
                    self._device.delay(0.5)
                    break
                if self._device(resourceId="com.tcl.android.launcher:id/clearAll").exists:
                    self._device (resourceId="com.tcl.android.launcher:id/clearAll").click()
                self._device.delay(1)
            if self._device(resourceId="com.tcl.android.launcher:id/workspace").exists:
                self._logger.info("Clear all recent apps success")
                return True        
        except Exception:
            self.save_fail_img()
            common.log_traceback(traceback.format_exc())
                    


if __name__ == "__main__":
    d = Device("2ca4e829")
    c = Common(d)
    c.enterApp("Radio")
