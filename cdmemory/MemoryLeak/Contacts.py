import unittest, traceback
from lib.PSSValue import SampleAndReport
import time
from lib import common
from lib.getconfigs import GetConfigs
from lib.contactModule import Contacts
logger = common.createlogger("MAIN")
logger.debug("Connect devices")
mdevice = common.connect_device("MDEVICE")
# mdevice = common.connect_device("SWW4UW5XHUCA4L5H")
mCon = Contacts(mdevice, "Contacts")
cfg = GetConfigs("Contacts")
test_times = cfg.get_test_times()
logger.info("Trace Total Times " + str(test_times))


class ContactsCases(unittest.TestCase):
    pids = ['com.google.android.contacts']
    def setUp(self):
        mCon.backToHome()       
        self._name =  "Contacts_case_"+self._testMethodName+"_" + mCon.GetNowTime()
        self.sr = SampleAndReport(self.pids, sample=3, 
                                  caseName = self._name, 
                                  device = common.get_deviceId("MDEVICE"))
        self.sr.start()
        
    def tearDown(self):
        mCon.backToHome()
        self.sr.stop()
        for pid in self.pids:
            mCon.saveMeminfo(type = "End", 
                             packageName = pid, 
                             filename = self._name) 
        
    def testChangePhoto(self):        
        logger.info("ChangePhoto")
        startTime = time.time()
        while time.time() - startTime < test_times:
            try:
                if mCon.enter_contact() and mCon.enter_create_contact() and mCon.changePhoto("takePhoto") \
                and mCon.changePhoto("choosePhoto") and mCon.discard_contact():
                    mCon.backToHome()
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("Contacts test fail!")
                    mCon.save_fail_img()
            except Exception:
                mCon.save_fail_img()
                logger.warning("Contacts test Exception!")
                common.log_traceback(traceback.format_exc())
                mCon.backToHome()     
        
        
    def testSwipeContacts(self):        
        startTime = time.time()
        logger.info("Swipe Contacts")
        if mCon.enter_contact():
            while time.time() - startTime < test_times:
                try:
                    if mCon.swipeContacts():                        
                        logger.info("Trace Success Loop")
                    else:
                        logger.warning("Contacts test fail!")
                        mCon.save_fail_img()
                except Exception:
                    mCon.save_fail_img()
                    logger.warning("Contacts test Exception!")
                    common.log_traceback(traceback.format_exc())
                    mCon.backToHome()
                    mCon.enter_contact()
                    
                    
        mCon.backToHome()  
        
    def testFindContact(self):
        startTime = time.time()
        logger.info("Find Contact")
        if mCon.enter_contact():
            while time.time() - startTime < test_times:
                try:
                    if mCon.findContact():
                        logger.info("Trace Success Loop ")
                    else:
                        logger.warning("Contacts test fail!")
                        mCon.save_fail_img()
                        
                    if mdevice(resourceId = "com.tct.contacts:id/search_back_button").exists:
                        mdevice(resourceId = "com.tct.contacts:id/search_back_button").click()
                        mdevice.delay(2)
                    else:
                        mCon.backToHome()
                        mCon.enter_contact()
                except Exception:
                    mCon.save_fail_img()
                    logger.warning("Contacts test Exception!")
                    common.log_traceback(traceback.format_exc())
                    mCon.backToHome()
                    mCon.enter_contact()
                    
        mCon.backToHome()
        
    def testCallContact(self):
        startTime = time.time()
        logger.info("Call Contact")
        
        while time.time() - startTime < test_times:
            try:
                if mCon.enter_contact() and mCon.testCallContact():
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("Contacts test fail!")
                    mCon.save_fail_img()
                    
                mCon.backToHome()    
            except Exception:
                mCon.save_fail_img()
                logger.warning("Contacts test Exception!")
                common.log_traceback(traceback.format_exc())
                mCon.backToHome()                
                           
    def testReEnterContact(self):
        startTime = time.time()
        logger.info("ReEnter Contact")
        mCon.clearAllRecent()
        while time.time() - startTime < test_times:
            try:
                if mCon.enter_contact():
                    mCon.backToHome() 
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("Contacts test fail!")
                    mCon.save_fail_img()
                                      
            except Exception:
                mCon.save_fail_img()
                logger.warning("Contacts test Exception!")
                common.log_traceback(traceback.format_exc())
                mCon.backToHome()
                            
    def testReEnterDetailsContact(self):
        startTime = time.time()
        logger.info("ReEnter Details Contact")
        mCon.clearAllRecent()
        while time.time() - startTime < test_times:
            try:
                if mCon.enter_contact() and mCon.testReEnterDetailsContact():
                    mCon.backToHome()  
                    logger.info("Trace Success Loop ")
                else:
                    logger.warning("Contacts test fail!")
                    mCon.save_fail_img()
                                      
            except Exception:
                mCon.save_fail_img()
                logger.warning("Contacts test Exception!")
                common.log_traceback(traceback.format_exc())
                mCon.backToHome()
                
    def testEnterContactByRecent(self):
        startTime = time.time()
        logger.info("ReEnter Contact")
        mCon.clearAllRecent()
        while time.time() - startTime < test_times:
            try:
                if mCon.testEnterContactByRecent():  
                    logger.info("Trace Success Loop")
                else:
                    logger.warning("Contacts test fail!")
                    mCon.save_fail_img()
                                      
            except Exception:
                mCon.save_fail_img()
                logger.warning("Contacts test Exception!")
                common.log_traceback(traceback.format_exc())
                mCon.backToHome()
                            
if __name__ == "__main__":    
    common.runTest(ContactsCases, [
                                    "testChangePhoto",
                                    "testSwipeContacts",
                                    "testFindContact",
                                    "testCallContact",
                                    "testReEnterContact",
                                    "testReEnterDetailsContact",
                                    "testEnterContactByRecent"
                                  ])
