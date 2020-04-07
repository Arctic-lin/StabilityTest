# -*- coding: UTF-8 -*-

import unittest, traceback
from lib.PSSValue import SampleAndReport
#from uiautomator import Device
import time
from lib import common
from lib.getconfigs import GetConfigs
from lib.callModule import Call

logger = common.createlogger("MAIN")
logger.debug("Connect devices")
mdevice= common.connect_device("MDEVICE")
mdevice = common.connect_device("GAWKFQT8WGL7L7S8")
mCall = Call(mdevice, "mCall")

cfg = GetConfigs("Call")

test_times = cfg.get_test_times()
    
logger.info("Trace Total Times " + str(test_times))

class CallTestCase(unittest.TestCase):   
    pids = ["com.google.android.dialer"]
    
    def setUp(self):
        mCall.backToHome()
        mCall.enter_call()        
        self._name ="Call_case_"+ self._testMethodName+"_"+mCall.GetNowTime()
        self.sr = SampleAndReport(self.pids, sample=3, 
                                  caseName = self._name,
                                  device = common.get_deviceId("MDEVICE"))
        self.sr.start()
        
    def tearDown(self):
        mCall.backToHome()
        self.sr.stop()
        for pid in self.pids:
            mCall.saveMeminfo(type = "End", 
                             packageName = pid, 
                             filename = self._name) 
        
    def testContDialFromDifMode(self):
        logger.debug("Start to Call from different mode.")
        if not mCall.enter_call():
            mCall.enter_call() 
        startTime = time.time()
        logger.info("ContDialFromDifMode")
        while time.time() - startTime < test_times:
            try:                
                if mCall.callFromDifMode():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("ContDialFromDifMode test failed.")
            except Exception:
                mCall.save_fail_img()
                logger.warning("ContDialFromDifMode Exception!")
                common.log_traceback(traceback.format_exc())
                mCall.backToHome()
    
    def testSwitchAndInvokeRecent(self):
        mCall.clearAllRecent()
        logger.debug("Start to SwitchAndInvokeRecent.")
        if not mCall.enter_call():
            mCall.enter_call() 
        startTime = time.time()
        logger.info("SwitchAndInvokeRecent")
        while time.time() - startTime < test_times:
            try:                
                if mCall.switchBackAndInvokeFromRecent():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("SwitchAndInvokeRecent test failed.")
            except Exception:
                mCall.save_fail_img()
                logger.warning("SwitchAndInvokeRecent Exception!")
                common.log_traceback(traceback.format_exc())
                mCall.backToHome()
    
    def testSwitchListInCall(self):
        logger.debug("Start to SwitchListInCall.")
        if not mCall.enter_call():
            mCall.enter_call() 
        startTime = time.time()
        logger.info("SwitchListInCall") 
        while time.time() - startTime < test_times:
            try:                
                mCall._device(text="Favorites").click()
                mCall._device.delay(1)
                mCall._device(text="Recents").click()
                mCall._device.delay(1)
                mCall._device(text="Contacts").click()
                mCall._device.delay(1)
                logger.info("Trace Success Loop")
            except Exception:
                mCall.save_fail_img()
                logger.warning("SwitchListInCall Exception!")
                common.log_traceback(traceback.format_exc())
                mCall.backToHome()

    def testLargerCalllog(self):
        logger.debug("Start to LargerCalllog.")
        if not mCall.enter_call():
            mCall.enter_call() 
        startTime = time.time()
        logger.info("LargerCalllog") 
        while time.time() - startTime < test_times:
            if not mCall.enter_call():
                mCall.enter_call() 
            try:                
                mCall.swipeInCalls()
                mCall.enterDetailsAndCall()
                mCall.deleteRecentCalls()
                
                logger.info("Trace Success Loop")
            except Exception:
                mCall.save_fail_img()
                logger.warning("testLargerCalllog Exception!")
                common.log_traceback(traceback.format_exc())
                mCall.backToHome()  

    def testMatchPhoneNumber(self):
        logger.debug("Start to testMatchPhoneNumber.")
        if not mCall.enter_call():
            mCall.enter_call() 
        startTime = time.time()
        logger.info("MatchPhoneNumber")
        while time.time() - startTime < test_times:
            try:
                if mCall.findAndCheckPhoneNumbers():                    
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("testMatchPhoneNumber test failed.")
            except Exception:
                mCall.save_fail_img()
                logger.warning("testMatchPhoneNumber Exception!")
                common.log_traceback(traceback.format_exc())
                mCall.backToHome()            
                 

if __name__ == "__main__":
    common.runTest(CallTestCase, [
                                "testContDialFromDifMode",
                                "testSwitchAndInvokeRecent",
                                "testSwitchListInCall",
                                "testMatchPhoneNumber",
                                "testLargerCalllog",
                                 ])    
    
    